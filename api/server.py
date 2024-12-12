import os
import requests
from flask import Flask, request, jsonify
from PIL import Image
import time
import subprocess

app = Flask(__name__)

INPUT_FOLDER = "/tmp/input"
OUTPUT_FOLDER = "/tmp/output"
SCRIPT_DIR = "."
IMAGE_NAME = "image.png"
GIF_NAME = "downloaded.gif"
MAX_RETRIES = 5
NSFW_API_URL = "https://demo.api4ai.cloud/nsfw/v1/results"

SCRIPT_MAPPING = {
    'high': 'high.py',
    'low': 'low.py',
    'mid': 'mid.py',
    'ehigh': 'extra-high.py',
    'elow': 'extra-low.py',
    'nsfw': 'NSFW.py',
}

def classify_image(image_url):
    api_data = {"url": image_url}
    try:
        response = requests.post(NSFW_API_URL, data=api_data)
        if response.status_code == 200:
            result = response.json()
            classifications = result.get("results", [])[0].get("entities", [])[0].get("classes", {})
            nsfw_score = classifications.get("nsfw", 0) * 100
            sfw_score = classifications.get("sfw", 0) * 100
            if nsfw_score > 45:
                return "NSFW", nsfw_score, sfw_score
            elif sfw_score > 45:
                return "SFW", nsfw_score, sfw_score
            else:
                return "Uncertain", nsfw_score, sfw_score
        else:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    except Exception as e:
        raise Exception(f"Classification error: {str(e)}")

def save_image_from_url(image_url, image_path):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                if response.status_code == 503 and attempt < MAX_RETRIES - 1:
                    continue
                return False
        except Exception as e:
            return False

def run_script(script_name):
    script_path = os.path.join(SCRIPT_DIR, script_name)
    try:
        os.system(f"python3 {script_path}")
        return True
    except Exception as e:
        return False

def get_lua_script(output_file):
    try:
        with open(output_file, 'r') as f:
            lua_script = f.read()
        return lua_script
    except Exception as e:
        return None

def download_gif(gif_url, temp_folder):
    os.makedirs(temp_folder, exist_ok=True)
    gif_filename = os.path.join(temp_folder, GIF_NAME)
    
    response = requests.get(gif_url)
    if response.status_code == 200:
        with open(gif_filename, "wb") as f:
            f.write(response.content)
        return gif_filename
    else:
        return None

def extract_frames(gif_path, output_folder, fps="max"):
    os.makedirs(output_folder, exist_ok=True)
    with Image.open(gif_path) as gif:
        total_frames = gif.n_frames
        frames = []
        
        if fps == "max":
            frame_interval = 1
        elif fps == 1:
            frame_interval = gif.info['duration'] / 1000
        else:
            frame_interval = gif.n_frames / fps
        
        for i in range(0, total_frames, int(frame_interval)):
            gif.seek(i)
            frame_path = os.path.join(output_folder, f"frame_{i}.png")
            gif.save(frame_path, format="PNG")
            frames.append(frame_path)
    
    return frames

def upload_image_to_imgbb(api_key, image_path):
    url = "https://api.imgbb.com/1/upload"
    payload = {"key": api_key}
    
    with open(image_path, "rb") as image_file:
        files = {"image": image_file}
        response = requests.post(url, data=payload, files=files)
    
    if response.status_code == 200:
        result = response.json()
        return result['data']['url']
    else:
        return None

def process_and_upload_gif(api_key, gif_url, output_folder, fps="max"):
    temp_folder = "/tmp/processed_gif"
    
    gif_path = download_gif(gif_url, temp_folder)
    if not gif_path:
        return []
    
    frames = extract_frames(gif_path, output_folder, fps)
    uploaded_urls = []
    
    for image_file in frames:
        url = upload_image_to_imgbb(api_key, image_file)
        if url:
            uploaded_urls.append(url)
        time.sleep(1 / fps if fps != "max" else 0.1)
    
    return uploaded_urls

def execute_gif_sender(uploaded_urls):
    try:
        result = subprocess.run(
            ['python3', 'gif-sender.py'] + uploaded_urls,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except Exception:
        return None

@app.route('/send_image', methods=['POST'])
def send_image():
    data = request.get_json()
    if not data or not data.get('image_url') or not data.get('button_clicked'):
        return jsonify({"status": "error", "message": "Missing image_url or button_clicked"}), 400

    image_url = data['image_url']
    button_clicked = data['button_clicked']

    try:
        classification, nsfw_score, sfw_score = classify_image(image_url)
        
        if classification == "NSFW":
            if run_script(SCRIPT_MAPPING['nsfw']):
                return jsonify({"status": "success", "message": "NSFW script executed"}), 200
            else:
                return jsonify({"status": "error", "message": "Error executing NSFW script"}), 500

        elif classification == "SFW":
            os.makedirs(INPUT_FOLDER, exist_ok=True)
            image_path = os.path.join(INPUT_FOLDER, IMAGE_NAME)

            if not save_image_from_url(image_url, image_path):
                return jsonify({"status": "error", "message": "Failed to download image"}), 400

            if not run_script(SCRIPT_MAPPING.get(button_clicked)):
                return jsonify({"status": "error", "message": f"Error executing script for button {button_clicked}"}), 500

            output_file = os.path.join(OUTPUT_FOLDER, IMAGE_NAME.replace('.png', '.lua'))
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            lua_script = get_lua_script(output_file)
            if lua_script:
                return jsonify({"status": "success", "lua_script": lua_script})
            else:
                return jsonify({"status": "error", "message": "Error reading Lua script"}), 500

        else:
            return jsonify({"status": "error", "message": "Image classification is uncertain"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/send_gif', methods=['POST'])
def send_gif():
    data = request.get_json()

    if not data or not data.get('gif_url') or not data.get('api_key'):
        return jsonify({"status": "error", "message": "Missing gif_url or api_key"}), 400

    gif_url = data['gif_url']
    api_key = data['api_key']
    
    uploaded_urls = process_and_upload_gif(api_key, gif_url, OUTPUT_FOLDER)

    if uploaded_urls:
        gif_sender_output = execute_gif_sender(uploaded_urls)
        
        if gif_sender_output:
            return jsonify({"status": "success", "uploaded_urls": uploaded_urls, "gif_sender_output": gif_sender_output})
        else:
            return jsonify({"status": "error", "message": "Error executing gif-sender.py"}), 500
    else:
        return jsonify({"status": "error", "message": "Failed to process and upload GIF frames"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ["true", "1"]
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

import os
import subprocess
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

INPUT_FOLDER = "/tmp/input"
OUTPUT_FOLDER = "/tmp/output"
SCRIPT_DIR = "."
IMAGE_NAME = "image.png"
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

@app.route('/send_image', methods=['POST'])
def send_image():
    data = request.get_json()

    if not data or not data.get('image_url') or not data.get('button_clicked'):
        return jsonify({"status": "error", "message": "Missing image_url or button_clicked"}), 400

    image_url = data['image_url']
    button_clicked = data['button_clicked']
    
    text_api_url = "https://api.sightengine.com/1.0/check.json"
    text_api_params = {
        "models": "offensive,text-content",
        "api_user": "1726990225",
        "api_secret": "YGaA9jJn5sipbN5TC3GDBD7YJro5UnZx",
        "url": image_url
    }

    try:
        text_response = requests.get(text_api_url, params=text_api_params)
        if text_response.status_code == 200:
            text_result = text_response.json()
            text_content = text_result.get("text", {}).get("text", "")
            profanities = text_result.get("text", {}).get("profanity", [])

            print("Text Analysis Result:")
            print("Text Content:", text_content)
            print("Profanities Detected:", profanities)

            high_intensity_discriminatory = any(
                profanity.get("type") == "discriminatory" and profanity.get("intensity") == "high"
                for profanity in profanities
            )

            offensive_detected = any(
                profanity.get("type") == "offensive" or profanity.get("type") == "sexual"
                for profanity in profanities
            )

            if high_intensity_discriminatory or offensive_detected:
                subprocess.run(["python3", "NSFW.py"])
                return jsonify({"message": "Offensive or sexual content detected. NSFW script executed."}), 400
        else:
            return jsonify({
                "error": f"Text API request failed with status code {text_response.status_code}",
                "details": text_response.text
            }), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ["true", "1"]
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

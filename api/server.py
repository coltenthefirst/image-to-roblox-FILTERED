from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import tempfile

app = Flask(__name__)
CORS(app)

SCRIPT_DIR = "."
MAX_RETRIES = 3
SCRIPT_MAPPING = {
    'high': 'high.py',
    'low': 'low.py',
    'mid': 'mid.py',
    'ehigh': 'extra-high.py',
    'elow': 'extra-low.py',
}

def save_image_from_url(image_url):
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Attempting to download image from {image_url} (Attempt {attempt + 1})")
            response = requests.get(image_url)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file.write(response.content)
                    temp_image_path = tmp_file.name
                print(f"Image saved to {temp_image_path}")
                return temp_image_path
            else:
                print(f"Failed to download image: {response.status_code} {response.text}")
                if response.status_code == 503 and attempt < MAX_RETRIES - 1:
                    print("Retrying...")
                    continue
                return None
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

def run_script(button_clicked):
    selected_script = SCRIPT_MAPPING.get(button_clicked)
    if selected_script:
        script_path = os.path.join(SCRIPT_DIR, selected_script)
        try:
            print(f"Executing script: {selected_script}")
            os.system(f"python3 {script_path}")
            return True
        except Exception as e:
            print(f"Error running script: {e}")
            return False
    return False

def get_lua_script(output_file):
    try:
        with open(output_file, 'r') as f:
            lua_script = f.read()
        print(f"Successfully read Lua script from {output_file}")
        return lua_script
    except Exception as e:
        print(f"Error reading output Lua file: {e}")
        return None

@app.route('/send_image', methods=['POST'])
def send_image():
    print("Received POST request to /send_image")
    data = request.get_json()
    print(f"Raw data received: {data}")

    if not data or not data.get('image_url') or not data.get('button_clicked'):
        print("Error: Missing image_url or button_clicked")
        return jsonify({"status": "error", "message": "Missing image_url or button_clicked"}), 400

    image_url = data['image_url']
    button_clicked = data['button_clicked']

    temp_image_path = save_image_from_url(image_url)
    if not temp_image_path:
        return jsonify({"status": "error", "message": "Failed to download image"}), 400

    if not run_script(button_clicked):
        return jsonify({"status": "error", "message": f"Error executing script for button {button_clicked}"}), 500

    output_file = os.path.join(SCRIPT_DIR, "output.lua")

    lua_script = get_lua_script(output_file)
    if lua_script:
        return jsonify({"status": "success", "lua_script": lua_script})
    else:
        return jsonify({"status": "error", "message": "Error reading Lua script"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
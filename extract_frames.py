import os
from PIL import Image
import sys
import subprocess
import requests

NSFW_API_URL = "https://demo.api4ai.cloud/nsfw/v1/results"
TEXT_API_URL = "https://api.sightengine.com/1.0/check.json"
NSFW_THRESHOLD = 45

def classify_image(image_path):
    api_data = {"url": image_path}
    try:
        response = requests.post(NSFW_API_URL, data=api_data)
        if response.status_code == 200:
            result = response.json()
            classifications = result.get("results", [])[0].get("entities", [])[0].get("classes", {})
            nsfw_score = classifications.get("nsfw", 0) * 100
            if nsfw_score > NSFW_THRESHOLD:
                return "NSFW"
            return "SFW"
        else:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    except Exception as e:
        raise Exception(f"Classification error: {str(e)}")

def check_text_content(image_url):
    text_api_params = {
        "models": "offensive,text-content",
        "api_user": "1726990225",
        "api_secret": "YGaA9jJn5sipbN5TC3GDBD7YJro5UnZx",
        "url": image_url
    }
    try:
        text_response = requests.get(TEXT_API_URL, params=text_api_params)
        if text_response.status_code == 200:
            text_result = text_response.json()
            profanities = text_result.get("text", {}).get("profanity", [])
            for profanity in profanities:
                if profanity.get("type") in ["offensive", "sexual"]:
                    return True
            return False
        else:
            raise Exception(f"Text API request failed with status code {text_response.status_code}")
    except Exception as e:
        raise Exception(f"Text classification error: {str(e)}")

def extract_frames(gif_path, output_folder, fps="10"):
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

def process_frames(frames):
    for frame_path in frames:
        classification = classify_image(frame_path)
        if classification == "NSFW":
            subprocess.run(["python3", "NSFW.py"])
            print(f"NSFW content detected in frame {frame_path}. Process stopped.")
            return False
        if check_text_content(frame_path):
            subprocess.run(["python3", "NSFW.py"])
            print(f"Offensive or sexual text detected in frame {frame_path}. Process stopped.")
            return False
    return True

if __name__ == "__main__":
    gif_path = sys.argv[1]
    output_folder = sys.argv[2]
    fps = sys.argv[3]
    
    frames = extract_frames(gif_path, output_folder, fps)
    if frames:
        print(f"Extracted {len(frames)} frames.")
        if not process_frames(frames):
            sys.exit(1)
        subprocess.run(["python3", "upload_frames.py", output_folder, "your_imgbb_api_key"])
    else:
        print("Failed to extract frames.")
        sys.exit(1)

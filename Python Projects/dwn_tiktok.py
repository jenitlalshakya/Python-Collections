import requests
import os

def download_tiktok_no_watermark():
    url = input("Enter tiktok video url: ").strip()
    api_url = f"https://www.tikwm.com/api/?url={url}"
    print("Processing...")

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if "data" in data and "play" in data["data"]:
            video_url = data["data"]["play"]
            username = data["data"]["author"].get("unique_id", "unknown")
            video_id = data["data"].get("id", "noid")
            save_path = r"D:\Tiktok Videos"

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            filename = f"{username}_{video_id}.mp4"
            full_path = os.path.join(save_path, filename)

            print("Downloading...")

            video_content = requests.get(video_url).content
            
            with open(full_path, "wb") as f:
                f.write(video_content)

            print(f"Download complete: {full_path}")
        else:
            print("Could not find video URL")
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    download_tiktok_no_watermark()
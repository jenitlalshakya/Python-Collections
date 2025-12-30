import requests
import os

def download_tiktok_no_watermark():
    url = input("Enter tiktok video url: ").strip()
    api_url = f"https://www.tikwm.com/api/?url={url}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if "data" in data:
            content_type = data["data"].get("type", 0)
            username = data["data"]["author"].get("unique_id", "unknown")
            video_id = data["data"].get("id", "noid")
            save_path = r"D:\Tiktok Videos"

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            if content_type == 0 and "play" in data["data"]:
                video_url = data["data"]["play"]
                filename = f"{username}_{video_id}.mp4"
                full_path = os.path.join(save_path, filename)

                video_content = requests.get(video_url).content

                with open(full_path, "wb") as f:
                    f.write(video_content)

                print(f"Video downloaded: {full_path}")
            
            elif content_type == 1 and "image" in data["data"]:
                image_urls = data["data"]["image"]

                for i, img_url in enumerate(image_urls, start=1):
                    filename = f"{username}_{video_id}_{i}.jpg"
                    full_path = os.path.join(save_path, filename)
                    img_content = requests.get(img_url).content

                    with open(full_path, "wb") as f:
                        f.write(img_content)
                print(f"{len(image_urls)} image(s) downloaded to {save_path}")

        else:
            print("Could not find video or image URL")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    download_tiktok_no_watermark()
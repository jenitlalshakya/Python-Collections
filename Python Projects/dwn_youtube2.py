from pytubefix import YouTube
from urllib.parse import urlparse, parse_qs
import os


def clean_youtube_url(url: str) -> str:
    parsed = urlparse(url)

    if "youtu.be" in parsed.netloc:
        video_id = parsed.path.lstrip("/")
    else:
        qs = parse_qs(parsed.query)
        video_id = qs.get("v", [None])[0]

    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    
    return url

def download(url, folder):
    os.makedirs(folder, exist_ok=True)

    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()

    try:
        stream.download(output_path=folder)
    except Exception as e:
        print(f"An error occured: {e}")
    
    print("Download Completed")


def main():
    url = input("Enter YouTube Video URL: ")
    folder = input("Enter folder location (Default: D:\\Youtue Videos): ").strip() or r"D:\Youtube Videos"
    clean_url = clean_youtube_url(url)
    download(clean_url, folder)



if __name__ == "__main__":
    main()
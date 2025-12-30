import yt_dlp
import os
from urllib.parse import urlparse, parse_qs
import imageio_ffmpeg as ffmpeg


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


def download_youtube_video():
    url = input("Enter the YOuTube video URL: ").strip()
    url = clean_youtube_url(url)
    folder = input("Enter folder path to save video (Default: D:\\Youtube Videos): ").strip() or r"D:\Youtube Videos"
    os.makedirs(folder, exist_ok=True)
    
    ffmpeg_path = ffmpeg.get_ffmpeg_exe()
    print("FFmpeg path:", ffmpeg_path)
    ydl_opts = {
        # "format": "best[ext=mp4][progressive=1]/best",
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook],
        "ffmpeg_location": ffmpeg_path,
        # "postprocessors": [
        #     {
        #         "key": "FFmpegVideoConvertor",
        #         "preferedformat": "mp4",
        #         "preferedcodec": "aac",
        #     },
        #     {
        #         "key": "FFmpegEmbedSubtitle",
        #     },
        #     {
        #         "key": "FFmpegVideoConvertor",
        #         "preferedformat": "mp4",
        #         "preferedcodec": "aac",
        #     },
        # ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"Title: {info.get('title')}")
            ydl.download([url])
        print("Download Completed!")
    except Exception as e:
        print(f"An error occured: {e}")


def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading... {d.get('_percent_str', '').strip()} "
              f"at {d.get('_speed_str', '')}", "\r")
    elif d['status'] == 'finished':
        print("\n Download Finished, now post-processing...")


if __name__ == "__main__":
    download_youtube_video()
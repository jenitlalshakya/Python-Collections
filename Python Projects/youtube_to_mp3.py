from yt_dlp import YoutubeDL
import os
import imageio_ffmpeg

def download_mp3(url, output_path=r"D:\YouTube Musics"):
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'quiet': False,
        'ffmpeg_location': ffmpeg_path,
        'noplaylist': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        print("✅ Download complete!")

if __name__ == "__main__":
    url = input("Enter YouTube video URL: ")
    download_mp3(url)
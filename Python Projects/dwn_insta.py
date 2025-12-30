import instaloader

def download_instagram_video(url):
    loader = instaloader.Instaloader(dirname_pattern="D:/Instagram Videos")
    
    try:
        print("Processing...")

        shortcode = url.strip().split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        loader.download_post(post, target="instagram_video")
        print("Download complete!")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    video_url = input("Enter Instagram video URL: ").strip()
    download_instagram_video(video_url)

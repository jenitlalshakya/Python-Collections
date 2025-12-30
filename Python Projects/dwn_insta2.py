import instaloader

def download_instagram_media():
    video_url = input("Enter Instagram video URL: ").strip()

    loader = instaloader.Instaloader(
        dirname_pattern="D:/Instagram Videos",
        download_video_thumbnails=False,
        save_metadata=False,
        post_metadata_txt_pattern=""
    )
    
    try:
        print("Processing...")

        shortcode = video_url.strip().split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        loader.download_post(post, target="instagram_media")
        print("Download complete! (Only images/videos saved)")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    download_instagram_media()
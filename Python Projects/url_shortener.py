import pyshorteners

def url_shortener():
    try:
        long_url = input("Enter the URL for Shortening: ")
        shortener = pyshorteners.Shortener()
        short_url = shortener.tinyurl.short(long_url)
        print(f"The Shortened URL is: {short_url}")
    except Exception as e:
        print(f"Error found: {e}")

if __name__ == "__main__":
    url_shortener()
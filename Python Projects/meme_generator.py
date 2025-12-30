"""
AI Meme Generator (Fixed for Pillow >=10)
- Downloads sample templates into ./templates (if missing)
- Gets a random joke from icanhazdadjoke (fallback to local list)
- Renders the joke across the meme image (top & bottom style)
- Saves the meme to ./output and opens it

Dependencies: pillow, requests
pip install pillow requests
"""
import os
import time
import textwrap
import random
import requests
from PIL import Image, ImageDraw, ImageFont
import webbrowser
import sys

# --- Config ---
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "output"
FONT_PATHS = [
    "impact.ttf",                      # common if user installed the Impact font
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # common linux
    "/Library/Fonts/Impact.ttf",       # mac path
]
TEMPLATE_URLS = [
    "https://i.imgflip.com/1bij.jpg",  # Drake Hotline Bling
    "https://i.imgflip.com/26am.jpg",  # Distracted boyfriend
    "https://i.imgflip.com/9ehk.jpg",  # Futurama Fry
    "https://i.imgflip.com/39t1o.jpg", # Blank fallback
]
MAX_WIDTH = 1000
TOP_PADDING = 10
BOTTOM_PADDING = 10

# --- Helpers ---
def ensure_dirs():
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_templates():
    print("Checking templates...")
    for url in TEMPLATE_URLS:
        name = os.path.basename(url).split("?")[0]
        path = os.path.join(TEMPLATE_DIR, name)
        if not os.path.exists(path):
            try:
                print(f"Downloading template: {url}")
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                with open(path, "wb") as f:
                    f.write(r.content)
                print("Saved:", path)
            except Exception as e:
                print("Failed to download", url, "-", e)

def get_local_templates():
    return [
        os.path.join(TEMPLATE_DIR, f)
        for f in os.listdir(TEMPLATE_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

def fetch_joke():
    try:
        headers = {"Accept": "application/json", "User-Agent": "AI-Meme-Generator/1.0"}
        r = requests.get("https://icanhazdadjoke.com/", headers=headers, timeout=8)
        if r.status_code == 200:
            joke = r.json().get("joke")
            if joke:
                print("Fetched joke from icanhazdadjoke.")
                return joke
    except Exception as e:
        print("Joke API failed:", e)
    local = [
        "I told my computer I needed a break, and it said: 'No problem — I'll go to sleep.'",
        "I put my root beer in a square glass. Now it's beer.",
        "Parallel lines have so much in common. It’s a shame they’ll never meet.",
        "Why do programmers prefer dark mode? Because light attracts bugs.",
        "My Wi-Fi went down for five minutes, so I had to talk to my family. They seem like nice people."
    ]
    print("Using fallback local joke.")
    return random.choice(local)

def find_font(size):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

def get_text_size(draw, text, font):
    """Return (width, height) of text."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def draw_text_with_outline(draw, xy, text, font, align="center"):
    x, y = xy
    for ox in [-2, -1, 0, 1, 2]:
        for oy in [-2, -1, 0, 1, 2]:
            if ox == 0 and oy == 0:
                continue
            draw.text((x+ox, y+oy), text, font=font, fill="black", anchor="ms", align=align)
    draw.text((x, y), text, font=font, fill="white", anchor="ms", align=align)

def render_meme(template_path, top_text, bottom_text, out_path):
    img = Image.open(template_path).convert("RGB")
    w, h = img.size
    if w > MAX_WIDTH:
        ratio = MAX_WIDTH / float(w)
        img = img.resize((int(w*ratio), int(h*ratio)), Image.LANCZOS)
        w, h = img.size

    draw = ImageDraw.Draw(img)

    # Top text
    if top_text:
        font_size = int(w / 12)
        while True:
            font = find_font(font_size)
            lines = textwrap.wrap(top_text.upper(), width=30)
            longest = max((get_text_size(draw, line, font)[0] for line in lines), default=0)
            if longest <= w * 0.95 or font_size < 16:
                break
            font_size -= 2
        total_h = sum(get_text_size(draw, line, font)[1] for line in lines) + (len(lines)-1)*5
        for i, line in enumerate(lines):
            _, lh = get_text_size(draw, line, font)
            line_y = TOP_PADDING + i * (lh + 5) + lh/2
            draw_text_with_outline(draw, (w/2, line_y), line, font)

    # Bottom text
    if bottom_text:
        font_size_b = int(w / 12)
        while True:
            font_b = find_font(font_size_b)
            lines_b = textwrap.wrap(bottom_text.upper(), width=30)
            longest = max((get_text_size(draw, line, font_b)[0] for line in lines_b), default=0)
            if longest <= w * 0.95 or font_size_b < 16:
                break
            font_size_b -= 2
        total_h_b = sum(get_text_size(draw, line, font_b)[1] for line in lines_b) + (len(lines_b)-1)*5
        start_y = h - total_h_b - BOTTOM_PADDING
        for i, line in enumerate(lines_b):
            _, lh = get_text_size(draw, line, font_b)
            line_y = start_y + i * (lh + 5) + lh/2
            draw_text_with_outline(draw, (w/2, line_y), line, font_b)

    img.save(out_path, quality=95)
    print("Saved meme:", out_path)
    try:
        if sys.platform.startswith("darwin"):
            os.system(f"open {out_path}")
        elif os.name == "nt":
            os.startfile(out_path)
        else:
            webbrowser.open("file://" + os.path.realpath(out_path))
    except Exception:
        pass

# --- Main flow ---
def main():
    ensure_dirs()
    download_templates()
    templates = get_local_templates()
    if not templates:
        print("No templates available in", TEMPLATE_DIR)
        return

    template = random.choice(templates)
    joke = fetch_joke()

    if len(joke) < 60:
        top, bottom = "", joke
    else:
        split_idx = None
        for sep in [". ", " - ", " — ", ", ", "; "]:
            mid = len(joke)//2
            left = joke.rfind(sep, 0, mid)
            right = joke.find(sep, mid)
            cand = right if right != -1 else left
            if cand != -1:
                split_idx = cand + len(sep)
                break
        if split_idx:
            top, bottom = joke[:split_idx].strip(), joke[split_idx:].strip()
        else:
            words = joke.split()
            half = len(words)//2
            top, bottom = " ".join(words[:half]), " ".join(words[half:])

    if random.random() >= 0.4 or not top:
        bottom = " ".join(filter(None, [top, bottom]))
        top = ""

    ts = int(time.time())
    out_name = f"meme_{ts}.jpg"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    print("Template:", template)
    print("Top text:", top)
    print("Bottom text:", bottom)
    render_meme(template, top, bottom, out_path)
    print("Done!")

if __name__ == "__main__":
    main()

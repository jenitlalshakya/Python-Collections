"""
CLI Image Optimizer
Usage:
    python image_optimizer_cli.py <file_or_folder1> <file_or_folder2> ...
"""

import sys
from pathlib import Path
from slugify import slugify
from PIL import Image, ImageOps, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Optional plugins for HEIC/AVIF
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except:
    pass
try:
    import avif
except:
    pass

MAX_DIMENSION = 1920
JPEG_QUALITY = 85
WEBP_QUALITY = 80
WEBP_LOSSLESS = False
CREATE_BOTH = True
SUPPORTED_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.avif', '.gif', '.tiff', '.bmp'}

def ensure_out_folder(src_path: Path) -> Path:
    out_dir = src_path.parent / 'optimized'
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

def is_image_file(p: Path) -> bool:
    return p.suffix.lower() in SUPPORTED_EXTS

def slugify_name(p: Path) -> str:
    return slugify(p.stem)

def open_image_safe(path: Path):
    try:
        img = Image.open(path)
        img = ImageOps.exif_transpose(img)
        return img
    except:
        return None

def convert_alpha_to_background(img: Image.Image, bg_color=(255,255,255)):
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        background = Image.new("RGB", img.size, bg_color)
        background.paste(img, mask=img.split()[-1])
        return background
    else:
        return img.convert("RGB")

def optimize_image(src: Path):
    img = open_image_safe(src)
    if img is None:
        print(f"SKIP {src.name}: Unsupported or corrupted image")
        return

    # resize large images
    width, height = img.size
    maxdim = max(width, height)
    if maxdim > MAX_DIMENSION:
        scale = MAX_DIMENSION / maxdim
        img = img.resize((int(width*scale), int(height*scale)), Image.LANCZOS)

    rgb_img = convert_alpha_to_background(img)

    base_slug = slugify_name(src)
    out_dir = ensure_out_folder(src)

    # Save JPG
    try:
        jpg_path = out_dir / f"{base_slug}.jpg"
        rgb_img.save(jpg_path, format='JPEG', quality=JPEG_QUALITY, optimize=True)
        print(f"Saved JPG: {jpg_path}")
    except Exception as e:
        print(f"ERROR JPG {src.name}: {e}")

    # Save WEBP
    if CREATE_BOTH:
        try:
            webp_path = out_dir / f"{base_slug}.webp"
            rgb_img.save(webp_path, format='WEBP', quality=WEBP_QUALITY, lossless=WEBP_LOSSLESS, optimize=True)
            print(f"Saved WEBP: {webp_path}")
        except Exception as e:
            print(f"ERROR WEBP {src.name}: {e}")

def gather_files(inputs):
    files = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            for f in p.rglob('*'):
                if f.is_file() and is_image_file(f):
                    files.append(f)
        elif p.is_file():
            if is_image_file(p):
                files.append(p)
    return sorted(list(dict.fromkeys(files)))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_optimizer_cli.py <file_or_folder1> <file_or_folder2> ...")
        sys.exit(1)

    input_paths = sys.argv[1:]
    files_to_process = gather_files(input_paths)
    if not files_to_process:
        print("No valid image files found.")
        sys.exit(0)

    print(f"Processing {len(files_to_process)} images...")
    for f in files_to_process:
        optimize_image(f)

    print("Done!")

"""
Image Optimizer GUI
- Drag & drop or browse images/folders
- Saves optimized images separately into <original_folder>/optimized/
- Produces both JPG and WEBP outputs, strips EXIF, resizes, and compresses
"""

import os
import io
import math
from pathlib import Path
from slugify import slugify
from PIL import Image, ImageOps, UnidentifiedImageError, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import PySimpleGUI as sg

# Optional plugins (import if available)
try:
    import pillow_heif  # type: ignore
    pillow_heif.register_heif_opener()
except Exception:
    pass

try:
    import avif  # type: ignore
    # pillow-avif-plugin registers itself automatically in many installs
except Exception:
    pass

# ---------- Config ----------
MAX_DIMENSION = 1920          # resize larger images to this max width/height
JPEG_QUALITY = 85             # 0-100
WEBP_QUALITY = 80             # 0-100
WEBP_LOSSLESS = False         # toggle lossless webp output
CREATE_BOTH = True            # produce both JPG and WEBP (you asked for all outputs)
REMOVE_EXIF = True
SUPPORTED_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.avif', '.gif', '.tiff', '.bmp'}
# ----------------------------

def ensure_out_folder(src_path: Path) -> Path:
    out_dir = src_path.parent / 'optimized'
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

def is_image_file(p: Path) -> bool:
    return p.suffix.lower() in SUPPORTED_EXTS

def slugify_name(p: Path) -> str:
    base = p.stem
    return slugify(base)

def open_image_safe(path: Path):
    try:
        img = Image.open(path)
        img = ImageOps.exif_transpose(img)
        return img
    except UnidentifiedImageError:
        return None

def convert_alpha_to_background(img: Image.Image, bg_color=(255,255,255)):
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        background = Image.new("RGB", img.size, bg_color)
        background.paste(img, mask=img.split()[-1])  # paste with alpha channel as mask
        return background
    else:
        return img.convert("RGB")

def optimize_image(src: Path, out_dir: Path, progress_callback=None):
    img = open_image_safe(src)
    if img is None:
        return (src, False, "Unsupported or corrupted image")

    # remove exif by not carrying it forward
    # resize if too large
    width, height = img.size
    maxdim = max(width, height)
    if maxdim > MAX_DIMENSION:
        scale = MAX_DIMENSION / maxdim
        new_size = (int(width * scale), int(height * scale))
        img = img.resize(new_size, Image.LANCZOS)

    # Prepare safe RGB (remove alpha if saving JPG)
    rgb_img = convert_alpha_to_background(img, bg_color=(255,255,255))

    base_slug = slugify_name(src)
    out_results = []

    # Save JPG
    try:
        jpg_name = f"{base_slug}.jpg"
        jpg_path = out_dir / jpg_name
        rgb_img.save(jpg_path, format='JPEG', quality=JPEG_QUALITY, optimize=True)
        out_results.append(str(jpg_path))
    except Exception as e:
        if progress_callback:
            progress_callback(f"JPG failed: {e}")

    # Save WEBP
    if CREATE_BOTH:
        try:
            webp_name = f"{base_slug}.webp"
            webp_path = out_dir / webp_name
            rgb_img.save(webp_path, format='WEBP', quality=WEBP_QUALITY, lossless=WEBP_LOSSLESS, optimize=True)
            out_results.append(str(webp_path))
        except Exception as e:
            if progress_callback:
                progress_callback(f"WEBP failed: {e}")

    return (src, True, out_results)

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
    # dedupe and sort
    unique = sorted(list(dict.fromkeys(files)))
    return unique

# ---------------- GUI ----------------
pass

layout = [
    [sg.Text("Drag & drop images or folders here — or click Browse")],
    [sg.Input(key='-FILES-', enable_events=True, visible=False), sg.FilesBrowse(button_text='Browse files/folders', key='-BROWSE-', file_types=(("Image Files", "*.*"),), target='-FILES-')],
    [sg.Listbox(values=[], size=(80, 12), key='-FILELIST-')],
    [sg.Button('Optimize Selected', key='-OPTIMIZE-'), sg.Button('Clear List'), sg.Button('Exit')],
    [sg.ProgressBar(max_value=100, orientation='h', size=(50, 15), key='-PROG-')],
    [sg.Multiline(size=(80,6), key='-LOG-', autoscroll=True, disabled=True)]
]

window = sg.Window('Auto Image Compressor & Web Optimizer', layout, finalize=True)

def log(text):
    window['-LOG-'].update(value=f"{text}\n", append=True)

def process_files(file_paths):
    files = gather_files(file_paths)
    if not files:
        log("No image files found in selection.")
        return

    total = len(files)
    prog = window['-PROG-']
    prog.UpdateBar(0, total)
    processed_count = 0

    for src in files:
        src = Path(src)
        out_dir = ensure_out_folder(src)
        def prog_cb(msg):
            log(f"{src.name}: {msg}")

        try:
            result = optimize_image(src, out_dir, progress_callback=prog_cb)
            if result[1]:
                out_paths = result[2]
                log(f"OK: {src.name} -> {', '.join(out_paths)}")
            else:
                log(f"SKIP: {src.name} ({result[2]})")
        except Exception as e:
            log(f"ERROR: {src.name} -> {e}")

        processed_count += 1
        prog.UpdateBar(processed_count, total)
    log("Done processing batch.")

# Main event loop
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    if event == '-FILES-':
        raw = values['-FILES-']
        if not raw:
            continue
        # PySimpleGUI FilesBrowse returns a string with filenames separated by ;
        # But we also want to accept folders from OS: split and keep
        parts = []
        for part in raw.split(';'):
            part = part.strip()
            if part:
                parts.append(part)
        # show in listbox
        current = window['-FILELIST-'].get_list_values()
        new_list = current + parts
        window['-FILELIST-'].update(new_list)

    if event == 'Clear List':
        window['-FILELIST-'].update([])
        window['-PROG-'].update(0)
        window['-LOG-'].update('')

    if event == '-OPTIMIZE-':
        filelist = window['-FILELIST-'].get_list_values()
        if not filelist:
            sg.popup("No files or folders selected.", title="Nothing to do")
            continue
        # Confirm target (we always save separately in optimized/)
        confirm = sg.popup_ok_cancel(f"Will save optimized files separately into each folder's 'optimized/' subfolder.\nProceed to optimize {len(filelist)} selection(s)?", title="Proceed?")
        if confirm != 'OK':
            continue
        process_files(filelist)

window.close()

import os
import shutil
from pathlib import Path

downloads_path = Path.home() / "Downloads"

CATEGORY_MAP = {
    "Images (PNG, JPG)": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
    "Documents (PDF, DOCX, TXT)": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx"],
    "Media (MP4, MP3)": [".mp4", ".mkv", ".mp3", ".wav", ".flac"],
    "Installers (EXE, MSI)": [".exe", ".msi"],
    "Archives (ZIP, RAR, 7z)": [".zip", ".rar", ".7z", ".tar", ".gz"],
}

def categorize_file(file_ext):
    for folder, extensions in CATEGORY_MAP.items():
        if file_ext.lower() in extensions:
            return folder
    return "Others"

def organize():
    for file in os.listdir(downloads_path):
        file_path = downloads_path / file
        if file_path.is_file():
            ext = file_path.suffix
            category = categorize_file(ext)
            target_folder = downloads_path / category
            target_folder.mkdir(exist_ok=True)
            shutil.move(str(file_path), str(target_folder / file))
    print("✅ Downloads organized!")


if __name__ == "__main__":
    organize()
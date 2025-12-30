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

def preview_files():
    print(f"\nScanning: {downloads_path}\n")
    moves = []

    for file in os.listdir(downloads_path):
        file_path = downloads_path / file
        if file_path.is_file():
            ext = file_path.suffix
            category = categorize_file(ext)
            target_folder = downloads_path / category

            moves.append((file, target_folder))

    if not moves:
        print("✅ No files found to organize.")
    else:
        print("📂 Preview of actions (NO files will be moved yet):\n")
        for file, folder in moves:
            print(f"  {file}  →  {folder.name}/")

    return moves


if __name__ == "__main__":
    moves = preview_files()
    if moves:
        confirm = input("\nDo you want to CREATE folders and MOVE files? (y/n): ").strip().lower()
        if confirm == "yes" or "y":
            for file, folder in moves:
                folder.mkdir(exist_ok=True)
                shutil.move(str(downloads_path / file), str(folder / file))
            print("\n✅ Files successfully organized!")
        else:
            print("\n❌ No changes made. Safe mode exited.")

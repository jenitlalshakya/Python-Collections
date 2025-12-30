import os
import shutil
from pathlib import Path
from datetime import datetime

downloads_path = Path.home() / "Downloads"
log_file = downloads_path / "organizer_log.txt"

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
    moves = []
    print(f"\nScanning: {downloads_path}\n")
    for file in os.listdir(downloads_path):
        file_path = downloads_path / file
        if file_path.is_file():
            ext = file_path.suffix
            category = categorize_file(ext)
            target_folder = downloads_path / category
            moves.append((file, target_folder))
            print(f"  {file}  →  {target_folder.name}/")
    if not moves:
        print("✅ No files found to organize.")
    return moves

def move_files(moves):
    moved_files = []
    for file, folder in moves:
        folder.mkdir(exist_ok=True)
        src = downloads_path / file
        dst = folder / file
        shutil.move(str(src), str(dst))
        moved_files.append((dst, src))  # store for undo
        with open(log_file, "a") as f:
            f.write(f"{datetime.now()} MOVED: {file} → {folder.name}\n")
    print("\n✅ Files successfully organized!")
    return moved_files

def undo_moves(moved_files):
    for dst, src in moved_files:
        if dst.exists():
            shutil.move(str(dst), str(src))
            with open(log_file, "a") as f:
                f.write(f"{datetime.now()} UNDONE: {dst.name} → {downloads_path}\n")
    print("\n↩️ Last move undone successfully!")

if __name__ == "__main__":
    moves = preview_files()
    if moves:
        confirm = input("\nDo you want to MOVE files? (YES / NO): ").strip().lower()
        if confirm == "yes":
            moved_files = move_files(moves)
            undo = input("\nDo you want to UNDO the move? (YES / NO): ").strip().lower()
            if undo == "yes":
                undo_moves(moved_files)
        else:
            print("\n❌ No changes made. Safe mode exited.")

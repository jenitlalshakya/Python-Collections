import os

def inject_payload(file_path, payload):
    with open(file_path, "ab") as f:
        f.write(payload.encode())
    print(f"✅ Payload '{payload}' injected into {file_path}")
    search_payload(file_path, payload)

def clean_payload(file_path, output_path, target=None, remove_all=False):
    with open(file_path, "rb") as f:
        content = f.read()

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if remove_all:
        if ext in [".jpg", ".jpeg"]:
            marker = b"\xFF\xD9"
            index = content.find(marker)
            if index != -1:
                content = content[:index + 2]  # Keep only up to JPEG end marker
        elif ext == ".png":
            marker = b"IEND"
            index = content.find(marker)
            if index != -1:
                content = content[:index + 8]  # Keep only up to PNG IEND + CRC
        else:
            print("⚠️ Unsupported image type for full clean. Skipping.")
            return

        with open(output_path, "wb") as f:
            f.write(content)

        print(f"✅ Strong clean applied. File saved as {output_path}")

    elif target:
        target_bytes = target.encode()
        if target_bytes in content:
            content = content.replace(target_bytes, b"")
            with open(output_path, "wb") as f:
                f.write(content)
            print(f"✅ Removed all occurrences of '{target}' and saved as {output_path}")
        else:
            print(f"⚠️ Payload '{target}' not found in the image.")

    else:
        print("⚠️ Please specify target or remove_all=True to clean the image.")

    check_hidden_data(output_path)


def check_hidden_data(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    with open(file_path, "rb") as f:
        content = f.read()

    if ext in [".jpg", ".jpeg"]:
        marker = b"\xFF\xD9"
        index = content.find(marker)
        if index != -1 and index + 2 < len(content):
            hidden_bytes = content[index + 2:]
            print(f"⚠️ Hidden data found! ({len(hidden_bytes)} bytes)")
            print("Preview:", hidden_bytes.decode(errors="ignore")[:100], "...")
        else:
            print("✅ No hidden data found after JPEG end marker.")
    elif ext == ".png":
        marker = b"IEND"
        index = content.find(marker)
        if index != -1 and index + 8 < len(content):
            hidden_bytes = content[index + 8:]
            print(f"⚠️ Hidden data found! ({len(hidden_bytes)} bytes)")
            print("Preview:", hidden_bytes.decode(errors="ignore")[:100], "...")
        else:
            print("✅ No hidden data found after PNG end marker.")
    else:
        print("⚠️ Unsupported file type for hidden data check.")


def search_payload(file_path, payload):
    with open(file_path, "rb") as f:
        content = f.read()

    if payload.encode() in content:
        print(f"⚠️ Payload '{payload}' still exists in {file_path}!")
    else:
        print(f"✅ Payload '{payload}' not found in {file_path}.")


if __name__ == "__main__":
    file_path = input("Enter the image file path: ").strip()
    location = input("Where to save file(same/different): ").strip().lower()

    if location == "same":
        output_path = file_path
    elif location == "different":
        output_path = input("Enter the location: ").strip()

    if not os.path.exists(file_path):
        print("⚠️ File does not exist!")
        exit()

    action = input("Choose an action (inject/clean/check): ").strip().lower()

    if action == "inject":
        payload = input("Enter the payload to inject: ").strip()
        inject_payload(file_path, payload)

    elif action == "clean":
        choice = input("Remove specific payload or all hidden data? (specific/all): ").strip().lower()
        if choice == "specific":
            target = input("Enter the payload text to remove: ").strip()
            clean_payload(file_path, output_path, target=target)
        else:
            clean_payload(file_path, output_path, remove_all=True)

    elif action == "check":
        check_hidden_data(file_path)
        search = input("Do you want to search for a specific payload? (y/n): ").strip().lower()
        if search == "y":
            target = input("Enter the payload text to search: ").strip()
            search_payload(file_path, target)

    else:
        print("Invalid choice. Please type 'inject', 'clean', or 'check'.")
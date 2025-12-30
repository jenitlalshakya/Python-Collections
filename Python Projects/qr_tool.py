import qrcode
import cv2
from pyzbar.pyzbar import decode
import re
import os

def generate_qr(data, folder="./qrcodes", filename=None):
    if not filename:
        safe_name = re.sub(r'[^A-Za-z0-9]+', '_', data)[:20]
        filename = f"{safe_name}.png"

    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, filename)

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img.save(file_path)
    print(f"✅ QR Code saved as {filename}")

def read_qr(filename="qrcode.png"):
    img = cv2.imread(filename)
    codes = decode(img)

    if not codes:
        print("❌ No QR Code found in the image.")
        return

    for code in codes:
        data = code.data.decode("utf-8")
        print(f"📜 QR Data: {data}")

        if data.startswith("WIFI:"):
            wifi_info = parse_wifi_qr(data)
            print(f"📶 WiFi Network: {wifi_info['ssid']}")
            print(f"🔑 Password: {wifi_info['password']}")
            print(f"🔒 Security: {wifi_info['security']}")
            print(f"🙈 Hidden: {wifi_info['hidden']}")

def parse_wifi_qr(data):
    wifi_info = {"ssid": "", "password": "", "security": "", "hidden": "false"}
    try:
        parts = data[5:-2].split(";")
        for part in parts:
            if part.startswith("S:"):
                wifi_info["ssid"] = part[2:]
            elif part.startswith("P:"):
                wifi_info["password"] = part[2:]
            elif part.startswith("T:"):
                wifi_info["security"] = part[2:]
            elif part.startswith("H:"):
                wifi_info["hidden"] = part[2:]
    except Exception as e:
        print("⚠️ Failed to parse WiFi QR:", e)
    return wifi_info

if __name__ == "__main__":
    print("1. Generate Text/URL QR Code")
    print("2. Generate WiFi QR Code")
    print("3. Read QR Code")
    choice = input("Enter choice (1/2/3): ")

    if choice in ["1", "2"]:
        folder = input("Enter folder to save QR codes (default: ./qrcodes): ") or "qrcodes"

        if choice == "1":
            text = input("Enter text/URL to encode: ")
            generate_qr(text, folder)

        elif choice == "2":
            ssid = input("Enter WiFi SSID (network name): ")
            password = input("Enter WiFi Password (leave blank if none): ")
            security = input("Enter security type (WPA/WEP/nopass): ") or "WPA"
            hidden = input("Is the network hidden? (true/false): ") or "false"

            wifi_data = f"WIFI:T:{security};S:{ssid};P:{password};H:{hidden};;"
            generate_qr(wifi_data, folder, filename=f"wifi_{ssid}.png")

    elif choice == "3":
        filename = input("Enter QR image filename (e.g., ./qrcodes/myqr.png): ") or "qrcode.png"
        read_qr(filename)

    else:
        print("Invalid choice.")
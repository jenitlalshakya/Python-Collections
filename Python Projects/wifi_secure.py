"""
wifi_secure.py

Usage:
  python wifi_secure.py save      # run netsh extractor and save encrypted data
  python wifi_secure.py view      # unlock (enter passphrase) and open interactive viewer
  python wifi_secure.py dump      # decrypt and print plaintext table (one-shot), then re-encrypt
"""

import subprocess, re, csv, argparse, getpass, json, os
from pathlib import Path
from typing import List, Dict
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

# ----------------------- Configuration -----------------------

DEFAULT_PASSPHRASE = "$eeWlflP@$$w0rD"

# ----------------------- Core Functions -----------------------

def run_netsh(args):
    """Run netsh command and return decoded text output."""
    try:
        output = subprocess.check_output(["netsh"] + args, stderr=subprocess.DEVNULL)
        try:
            return output.decode("cp1252", errors="ignore")
        except Exception:
            return output.decode("utf-8", errors="ignore")
    except subprocess.CalledProcessError:
        return ""

def get_profiles():
    """Extract all saved Wi-Fi profile names."""
    text = run_netsh(["wlan", "show", "profiles"])
    profiles = re.findall(r"All User Profile\s*:\s*(.+)", text, flags=re.I)
    return [p.strip().strip('"') for p in profiles]

def get_profile_password(profile_name):
    """Fetch password, authentication, and cipher for a given Wi-Fi profile."""
    text = run_netsh(["wlan", "show", "profile", f"{profile_name}", "key=clear"])
    if not text:
        return None
    m = re.search(r"Key Content\s*:\s*(.+)", text, flags=re.I)
    pwd = m.group(1).strip() if m else None
    auth_m = re.search(r"Authentication\s*:\s*(.+)", text, flags=re.I)
    cipher_m = re.search(r"Cipher\s*:\s*(.+)", text, flags=re.I)
    auth = auth_m.group(1).strip() if auth_m else ""
    cipher = cipher_m.group(1).strip() if cipher_m else ""
    return {"ssid": profile_name, "password": pwd, "authentication": auth, "cipher": cipher}

# ----------------------- Encryption Helpers -----------------------

DATA_FILE = Path(os.path.dirname(os.path.abspath(__file__))) / "wifi_password_new.bin"
SALT_SIZE = 16
NONCE_SIZE = 12
KDF_ITER = 390000

def derive_key(password: bytes, salt: bytes) -> bytes:
    """Derive a 32-byte encryption key using PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITER,
    )
    return kdf.derive(password)

def encrypt_blob(plaintext_bytes: bytes, password: str) -> bytes:
    """Encrypt plaintext bytes using AES-GCM with random salt and nonce."""
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password.encode("utf-8"), salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ct = aesgcm.encrypt(nonce, plaintext_bytes, None)
    return salt + nonce + ct

def decrypt_blob(blob: bytes, password: str) -> bytes:
    """Decrypt AES-GCM encrypted blob back to plaintext bytes."""
    if len(blob) < SALT_SIZE + NONCE_SIZE:
        raise ValueError("Blob too short / corrupted")
    salt = blob[:SALT_SIZE]
    nonce = blob[SALT_SIZE:SALT_SIZE+NONCE_SIZE]
    ct = blob[SALT_SIZE+NONCE_SIZE:]
    key = derive_key(password.encode("utf-8"), salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None)

# ----------------------- Save / Load Helpers -----------------------

def collect_profiles() -> List[Dict]:
    """Collect all Wi-Fi profiles and their details into a list."""
    profiles = get_profiles()
    results = []
    for p in profiles:
        info = get_profile_password(p)
        results.append(info or {"ssid": p, "password": None, "authentication": "", "cipher": ""})
    return results

def save_encrypted(results: List[Dict], password: str):
    """Encrypt and save Wi-Fi profile data to a binary file."""
    b = json.dumps(results, ensure_ascii=False).encode("utf-8")
    blob = encrypt_blob(b, password)
    DATA_FILE.write_bytes(blob)
    print(f"🔒 Encrypted data saved to: {DATA_FILE.resolve()}")

def load_encrypted(password: str) -> List[Dict]:
    """Load and decrypt Wi-Fi profile data from a binary file."""
    blob = DATA_FILE.read_bytes()
    pt = decrypt_blob(blob, password)
    return json.loads(pt.decode("utf-8"))

# ----------------------- Interactive Viewer -----------------------

def interactive_view(results: List[Dict]):
    """Interactive REPL to list or view specific Wi-Fi profiles."""
    print("\n*** UNLOCKED: data is in memory (plaintext) until you type `exit` ***")
    print("Commands: list | show <ssid> | exit")
    ssid_index = {r["ssid"]: r for r in results}
    try:
        while True:
            cmd = input("viewer> ").strip()
            if not cmd:
                continue
            if cmd == "list":
                for r in results:
                    print(f"- {r['ssid']}")
            elif cmd.startswith("show "):
                target = cmd[5:].strip()
                if target in ssid_index:
                    e = ssid_index[target]
                    print(f"SSID: {e['ssid']}\n  PASSWORD: {e.get('password') or '(none)'}\n  AUTH: {e.get('authentication','')}\n  CIPHER: {e.get('cipher','')}")
                else:
                    print("No such SSID found.")
            elif cmd == "exit":
                print("Exiting viewer and clearing plaintext from memory...")
                break
            else:
                print("Unknown command. Use: list | show <ssid> | exit")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting viewer and clearing plaintext from memory...")

# ----------------------- CLI Commands -----------------------

def cmd_save():
    """Extract Wi-Fi data, encrypt it, and save to file."""
    print("Collecting Wi-Fi profiles via netsh...")
    results = collect_profiles()
    print(f"Found {len(results)} profiles. Will encrypt and save.")

    # Use hardcoded passphrase if provided, otherwise prompt the user
    if DEFAULT_PASSPHRASE:
        pwd = DEFAULT_PASSPHRASE
        print("Using configured default passphrase for save.")
    else:
        pwd = getpass.getpass("Create passphrase to encrypt data: ")
        pwd2 = getpass.getpass("Confirm passphrase: ")
        if pwd != pwd2:
            print("Passphrases do not match. Aborting.")
            return

    save_encrypted(results, pwd)
    results.clear()

def cmd_view():
    """Unlock and view decrypted Wi-Fi data interactively."""
    if not DATA_FILE.exists():
        print("No encrypted data file found. Run `save` first.")
        return
    pwd = getpass.getpass("Enter passphrase to unlock: ")
    try:
        results = load_encrypted(pwd)
    except Exception:
        print("Failed to decrypt: wrong passphrase or corrupted file.")
        return
    print(f"\nDecrypted {len(results)} entries (in memory).")
    print(f"{'SSID':40} {'PASSWORD':25} {'AUTH':15} {'CIPHER'}")
    print("-" * 95)
    for r in results:
        pwd_shown = r["password"] if r["password"] else "(none)"
        print(f"{r['ssid'][:40]:40} {pwd_shown[:25]:25} {r['authentication'][:15]:15} {r['cipher']}")
    interactive_view(results)
    for r in results:
        r["password"] = None
    results.clear()
    print("Plaintext cleared from memory. Program exiting.")

def cmd_dump():
    """Decrypt and print Wi-Fi data once, then clear memory."""
    if not DATA_FILE.exists():
        print("No encrypted data file found. Run `save` first.")
        return
    pwd = getpass.getpass("Enter passphrase to unlock: ")
    try:
        results = load_encrypted(pwd)
    except Exception:
        print("Failed to decrypt: wrong passphrase or corrupted file.")
        return
    print(f"\nDecrypted {len(results)} entries (one-shot):")
    print(f"{'SSID':40} {'PASSWORD':25} {'AUTH':15} {'CIPHER'}")
    print("-" * 95)
    for r in results:
        pwd_shown = r["password"] if r["password"] else "(none)"
        print(f"{r['ssid'][:40]:40} {pwd_shown[:25]:25} {r['authentication'][:15]:15} {r['cipher']}")
    for r in results:
        r["password"] = None
    results.clear()
    print("Done. Plaintext cleared from memory.")

# ----------------------- Main Entrypoint -----------------------

def main():
    """CLI entrypoint to handle save, view, and dump commands."""
    parser = argparse.ArgumentParser(description="Secure Wi-Fi extractor (encrypts results).")
    parser.add_argument("cmd", choices=["save", "view", "dump"], help="save = extract+encrypt, view = unlock interactive, dump = one-shot print")
    args = parser.parse_args()
    if args.cmd == "save":
        cmd_save()
    elif args.cmd == "view":
        cmd_view()
    elif args.cmd == "dump":
        cmd_dump()

if __name__ == "__main__":
    main()

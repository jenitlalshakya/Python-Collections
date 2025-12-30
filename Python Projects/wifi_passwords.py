"""
Extract saved Wi-Fi SSIDs and passwords on Windows using `netsh`.
Outputs to console and saves wifi_passwords.csv in the script directory.
"""

import subprocess
import re
import csv
from pathlib import Path

def run_netsh(args):
    """Run netsh with given args and return output as text (handles typical Windows encodings)."""
    try:
        output = subprocess.check_output(["netsh"] + args, stderr=subprocess.DEVNULL)
        # netsh outputs bytes; try cp1252 then utf-8 fallback
        try:
            return output.decode("cp1252", errors="ignore")
        except Exception:
            return output.decode("utf-8", errors="ignore")
    except subprocess.CalledProcessError:
        return ""

def get_profiles():
    text = run_netsh(["wlan", "show", "profiles"])
    # Match likes like:     All User Profile    :MyWiFi
    profiles = re.findall(r"All User Profile\s*:\s*(.+)", text)
    profiles = [p.strip().strip('"') for p in profiles]
    return profiles

def get_profile_password(profile_name):
    text = run_netsh(["wlan", "show", "profile", f"{profile_name}", "key=clear"])
    if not text:
        return None # couldn't fetch
    #Key Content        :mypassword
    m = re.search(r"Key Content\s*:\s*(.+)", text)
    pwd = m.group(1).strip() if m else None
    # Also pull authentication / cipher if present
    auth_m = re.search(r"Authentication\s*:\s*(.+)", text)
    cipher_m = re.search(r"Cipher\s*:\s*(.+)", text)
    auth = auth_m.group(1).strip() if auth_m else ""
    cipher = cipher_m.group(1).strip() if cipher_m else ""
    return {"ssid": profile_name, "password": pwd, "authentication": auth, "cipher": cipher}

def main():
    profiles = get_profiles()
    if not profiles:
        print("No Wi-Fi profiles found (or `netsh` output couldn't be read).")
        return
    
    results = []
    for p in profiles:
        info = get_profile_password(p)
        if info is None:
            # Could not read profile (permissions or other issue)
            results.append({"ssid": p, "password": None, "authentication": "", "cipher": ""})
        else:
            results.append(info)

    # print a simple table
    print(f"\nFound {len(results)} profile(s):\n")
    print(f"{'SSID':40} {'PASSWORD':25} {'AUTH':15} {'CIPHER'}")
    print("-" * 95)
    for r in results:
        pwd = r["password"] if r["password"] else "(not found/none)"
        print(f"{r['ssid'][:40]:40} {pwd[:25]:25} {r['authentication'][:15]:15} {r['cipher']}")

    # save CSV
    out = Path("wifi_passwords.csv")
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ssid", "password", "authentication", "cipher"])
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"\nSaved results to: {out.resolve()}")


if __name__ == "__main__":
    main()
    
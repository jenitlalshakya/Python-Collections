"""
vault_app.py
Password & Notes Vault (GUI) - Platform / id / password format
Requires: customtkinter, cryptography, pyperclip
Install: pip install customtkinter cryptography pyperclip
"""

import os
import json
import base64
import tkinter.messagebox as mb
from typing import List, Dict, Any

import customtkinter as ctk
import pyperclip

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

# -------------------------
# Constants & file paths
# -------------------------
VAULT_FILE = "vault.json"   # stores {"salt": "...", "data": "..."} where data is base64 encrypted bytes
KDF_ITERATIONS = 390000
SALT_SIZE = 16

# -------------------------
# Crypto helpers
# -------------------------
def generate_salt() -> bytes:
    return os.urandom(SALT_SIZE)

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a 32-byte key from password+salt suitable for Fernet (urlsafe base64).
    """
    password_bytes = password.encode('utf-8')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
        backend=default_backend()
    )
    key = kdf.derive(password_bytes)
    return base64.urlsafe_b64encode(key)

def encrypt_entries(entries: List[Dict[str, Any]], password: str, salt: bytes) -> bytes:
    key = derive_key(password, salt)
    f = Fernet(key)
    raw = json.dumps(entries, ensure_ascii=False).encode('utf-8')
    token = f.encrypt(raw)
    return token

def decrypt_entries(token: bytes, password: str, salt: bytes) -> List[Dict[str, Any]]:
    key = derive_key(password, salt)
    f = Fernet(key)
    raw = f.decrypt(token)
    return json.loads(raw.decode('utf-8'))

# -------------------------
# Vault IO
# -------------------------
def vault_exists() -> bool:
    return os.path.exists(VAULT_FILE)

def create_new_vault(password: str) -> None:
    salt = generate_salt()
    initial_entries: List[Dict[str, Any]] = []
    token = encrypt_entries(initial_entries, password, salt)
    blob = {
        "salt": base64.b64encode(salt).decode('ascii'),
        "data": base64.b64encode(token).decode('ascii')
    }
    with open(VAULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(blob, f)
    print("Vault created:", VAULT_FILE)

def load_vault_blob() -> Dict[str, str]:
    with open(VAULT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_vault_blob(salt: bytes, token: bytes) -> None:
    blob = {
        "salt": base64.b64encode(salt).decode('ascii'),
        "data": base64.b64encode(token).decode('ascii')
    }
    with open(VAULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(blob, f)

# -------------------------
# App GUI
# -------------------------
class VaultApp:
    def __init__(self, root):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.root = root
        self.root.title("Secure Vault")
        self.root.geometry("760x480")
        self.root.resizable(False, False)

        # State
        self.salt = None
        self.key_password = None
        self.entries: List[Dict[str, Any]] = []

        # Top frame: login / create
        self.frame_top = ctk.CTkFrame(root, height=120)
        self.frame_top.pack(fill="x", padx=12, pady=8)

        self.lbl_info = ctk.CTkLabel(self.frame_top, text="Unlock or Create Vault", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_info.grid(row=0, column=0, columnspan=3, pady=(8,6), padx=8, sticky="w")

        self.lbl_master = ctk.CTkLabel(self.frame_top, text="Master password:")
        self.lbl_master.grid(row=1, column=0, padx=(10,4), pady=6, sticky="e")
        self.entry_master = ctk.CTkEntry(self.frame_top, width=300, show="*")
        self.entry_master.grid(row=1, column=1, padx=4, pady=6, sticky="w")

        self.btn_unlock = ctk.CTkButton(self.frame_top, text="Unlock Vault", command=self.unlock_vault)
        self.btn_unlock.grid(row=1, column=2, padx=8, pady=6)
        self.btn_create = ctk.CTkButton(self.frame_top, text="Create New Vault", command=self.create_vault_flow)
        self.btn_create.grid(row=1, column=3, padx=8, pady=6)

        # Main area: left list + right details
        self.frame_main = ctk.CTkFrame(root)
        self.frame_main.pack(fill="both", expand=True, padx=12, pady=(0,12))

        # Left: search + list
        self.frame_left = ctk.CTkFrame(self.frame_main, width=260)
        self.frame_left.pack(side="left", fill="y", padx=(8,6), pady=8)
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_list())

        self.entry_search = ctk.CTkEntry(self.frame_left, placeholder_text="Search platform or id...", textvariable=self.search_var)
        self.entry_search.pack(fill="x", padx=10, pady=(10,6))

        self.listbox = ctk.CTkScrollableFrame(self.frame_left)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # Buttons under list
        self.btn_add = ctk.CTkButton(self.frame_left, text="+ Add Entry", command=self.open_add_entry)
        self.btn_add.pack(fill="x", padx=10, pady=(0,6))
        self.btn_delete = ctk.CTkButton(self.frame_left, text="Delete Selected", fg_color="transparent", command=self.delete_selected)
        self.btn_delete.pack(fill="x", padx=10, pady=(0,8))

        # Right: details
        self.frame_right = ctk.CTkFrame(self.frame_main)
        self.frame_right.pack(side="left", fill="both", expand=True, padx=(6,8), pady=8)

        self.detail_title = ctk.CTkLabel(self.frame_right, text="Entry Details", font=ctk.CTkFont(size=16, weight="bold"))
        self.detail_title.pack(anchor="nw", padx=12, pady=(12,4))

        self.txt_details = ctk.CTkTextbox(self.frame_right, width=420, height=260, state="disabled")
        self.txt_details.pack(padx=12, pady=(0,6))

        # Copy and Save buttons
        self.btn_copy = ctk.CTkButton(self.frame_right, text="Copy Password", command=self.copy_password)
        self.btn_copy.pack(side="left", padx=(12,6), pady=6)
        self.btn_edit = ctk.CTkButton(self.frame_right, text="Edit Selected", command=self.open_edit_selected)
        self.btn_edit.pack(side="left", padx=(6,6), pady=6)
        self.btn_lock = ctk.CTkButton(self.frame_right, text="Lock Vault", command=self.lock_vault)
        self.btn_lock.pack(side="right", padx=(6,12), pady=6)

        # Internal: map displayed items to entries
        self.display_widgets = []
        self.selected_index = None

        # Initially, disable main UI until unlock
        self.set_ui_locked(True)

    # -------------------------
    # UI helpers
    # -------------------------
    def set_ui_locked(self, locked: bool):
        state = "normal" if not locked else "disabled"
        for w in [self.entry_search, self.btn_add, self.btn_delete, self.txt_details, self.btn_copy, self.btn_edit, self.btn_lock]:
            try:
                w.configure(state=state)
            except Exception:
                pass
        # listbox children will be rebuilt when unlocked/locked

    def refresh_list(self):
        # clear listframe
        for child in self.listbox.winfo_children():
            child.destroy()
        self.display_widgets.clear()
        query = self.search_var.get().lower().strip()
        for i, e in enumerate(self.entries):
            label_text = f"{e.get('platform','')} — {e.get('id','')}"
            if query and query not in label_text.lower() and query not in e.get('password','').lower():
                continue
            btn = ctk.CTkButton(self.listbox, text=label_text, width=240, anchor="w",
                                command=lambda idx=i: self.select_entry(idx))
            btn.pack(fill="x", padx=6, pady=4)
            self.display_widgets.append(btn)

    def select_entry(self, index: int):
        self.selected_index = index
        e = self.entries[index]
        self.txt_details.configure(state="normal")
        self.txt_details.delete("0.0", "end")
        pretty = f"Platform: {e.get('platform','')}\nID: {e.get('id','')}\nPassword: {e.get('password','')}\n\nNotes:\n{e.get('notes','')}"
        self.txt_details.insert("0.0", pretty)
        self.txt_details.configure(state="disabled")

    # -------------------------
    # Vault flows
    # -------------------------
    def create_vault_flow(self):
        pw = self.entry_master.get().strip()
        if not pw:
            mb.showwarning("Master password", "Enter a master password to create a new vault.")
            return
        if vault_exists():
            if not mb.askyesno("Overwrite?", "Vault already exists. Overwrite and create a new empty vault?"):
                return
        create_new_vault(pw)
        mb.showinfo("Vault created", "New vault created. Use the same master password to unlock it.")
        # auto-unlock
        self.entry_master.delete(0, 'end')
        self.entry_master.insert(0, pw)
        self.unlock_vault()

    def unlock_vault(self):
        pw = self.entry_master.get().strip()
        if not pw:
            mb.showwarning("Master password", "Enter master password to unlock.")
            return
        if not vault_exists():
            mb.showerror("No vault found", "No vault file found. Create new vault first.")
            return
        try:
            blob = load_vault_blob()
            salt = base64.b64decode(blob["salt"])
            token = base64.b64decode(blob["data"])
            entries = decrypt_entries(token, pw, salt)
            if not isinstance(entries, list):
                raise ValueError("Invalid vault format")
            self.salt = salt
            self.key_password = pw
            self.entries = entries
            self.set_ui_locked(False)
            self.refresh_list()
            mb.showinfo("Unlocked", "Vault unlocked successfully.")
        except Exception as exc:
            mb.showerror("Failed to unlock", "Wrong password or vault corrupted.\n\n" + str(exc))

    def lock_vault(self):
        # clear sensitive state
        self.salt = None
        self.key_password = None
        self.entries = []
        self.selected_index = None
        self.search_var.set("")
        for child in self.listbox.winfo_children():
            child.destroy()
        self.txt_details.configure(state="normal")
        self.txt_details.delete("0.0", "end")
        self.txt_details.configure(state="disabled")
        self.set_ui_locked(True)
        mb.showinfo("Locked", "Vault locked.")

    def auto_save(self):
        """
        Re-encrypt current entries with known salt & key_password and save.
        """
        if not self.salt or not self.key_password:
            return
        token = encrypt_entries(self.entries, self.key_password, self.salt)
        save_vault_blob(self.salt, token)

    # -------------------------
    # Entry CRUD
    # -------------------------
    def open_add_entry(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Add Entry")
        win.geometry("420x320")
        ctk.CTkLabel(win, text="Platform:").pack(anchor="w", padx=12, pady=(12,4))
        ent_platform = ctk.CTkEntry(win, width=360)
        ent_platform.pack(padx=12)
        ctk.CTkLabel(win, text="ID / Account:").pack(anchor="w", padx=12, pady=(8,4))
        ent_id = ctk.CTkEntry(win, width=360)
        ent_id.pack(padx=12)
        ctk.CTkLabel(win, text="Password:").pack(anchor="w", padx=12, pady=(8,4))
        ent_pw = ctk.CTkEntry(win, width=360, show="*")
        ent_pw.pack(padx=12)
        ctk.CTkLabel(win, text="Notes (optional):").pack(anchor="w", padx=12, pady=(8,4))
        ent_notes = ctk.CTkTextbox(win, width=360, height=80)
        ent_notes.pack(padx=12, pady=(0,8))

        def add_and_close():
            platform = ent_platform.get().strip()
            idv = ent_id.get().strip()
            pw = ent_pw.get().strip()
            notes = ent_notes.get("0.0", "end").strip()
            if not platform or not idv or not pw:
                mb.showwarning("Missing fields", "Platform, ID, and Password are required.")
                return
            entry = {"platform": platform, "id": idv, "password": pw, "notes": notes}
            self.entries.append(entry)
            self.auto_save()
            self.refresh_list()
            win.destroy()

        ctk.CTkButton(win, text="Add Entry", command=add_and_close).pack(pady=8)

    def delete_selected(self):
        if self.selected_index is None:
            mb.showwarning("Select", "Select an entry first.")
            return
        if not mb.askyesno("Confirm delete", "Delete the selected entry?"):
            return
        del self.entries[self.selected_index]
        self.selected_index = None
        self.auto_save()
        self.refresh_list()
        self.txt_details.configure(state="normal")
        self.txt_details.delete("0.0", "end")
        self.txt_details.configure(state="disabled")
        mb.showinfo("Deleted", "Entry deleted.")

    def open_edit_selected(self):
        if self.selected_index is None:
            mb.showwarning("Select", "Select an entry first.")
            return
        e = self.entries[self.selected_index]
        win = ctk.CTkToplevel(self.root)
        win.title("Edit Entry")
        win.geometry("420x320")
        ctk.CTkLabel(win, text="Platform:").pack(anchor="w", padx=12, pady=(12,4))
        ent_platform = ctk.CTkEntry(win, width=360)
        ent_platform.pack(padx=12)
        ent_platform.insert(0, e.get("platform",""))
        ctk.CTkLabel(win, text="ID / Account:").pack(anchor="w", padx=12, pady=(8,4))
        ent_id = ctk.CTkEntry(win, width=360)
        ent_id.pack(padx=12)
        ent_id.insert(0, e.get("id",""))
        ctk.CTkLabel(win, text="Password:").pack(anchor="w", padx=12, pady=(8,4))
        ent_pw = ctk.CTkEntry(win, width=360, show="*")
        ent_pw.pack(padx=12)
        ent_pw.insert(0, e.get("password",""))
        ctk.CTkLabel(win, text="Notes (optional):").pack(anchor="w", padx=12, pady=(8,4))
        ent_notes = ctk.CTkTextbox(win, width=360, height=80)
        ent_notes.pack(padx=12, pady=(0,8))
        ent_notes.insert("0.0", e.get("notes",""))

        def save_and_close():
            platform = ent_platform.get().strip()
            idv = ent_id.get().strip()
            pw = ent_pw.get().strip()
            notes = ent_notes.get("0.0", "end").strip()
            if not platform or not idv or not pw:
                mb.showwarning("Missing fields", "Platform, ID, and Password are required.")
                return
            updated = {"platform": platform, "id": idv, "password": pw, "notes": notes}
            self.entries[self.selected_index] = updated
            self.auto_save()
            self.refresh_list()
            win.destroy()

        ctk.CTkButton(win, text="Save", command=save_and_close).pack(pady=8)

    def copy_password(self):
        if self.selected_index is None:
            mb.showwarning("Select", "Select an entry first.")
            return
        pwd = self.entries[self.selected_index].get("password","")
        if not pwd:
            mb.showwarning("No password", "No password found to copy.")
            return
        pyperclip.copy(pwd)
        mb.showinfo("Copied", "Password copied to clipboard. (Be careful!)")

# -------------------------
# Main
# -------------------------
def main():
    root = ctk.CTk()
    app = VaultApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

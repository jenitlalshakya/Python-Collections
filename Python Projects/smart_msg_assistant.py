"""
smart_msg_assistant.py

Natural-style message scheduler that sends to WhatsApp (Web).
Supports: names (saved contacts) OR phone numbers, scheduling with natural language,
per-command voice/silent flag, and scaffolding for Email & SMS.

Run:
    python smart_msg_assistant.py

Note: First run requires scanning WhatsApp Web QR code in the opened browser window.
"""

import re
import time
import threading
import urllib.parse
from datetime import datetime
import schedule
import dateparser
import pyttsx3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import logging

# ---------- Configuration ----------
DEFAULT_VOICE = False  # default if user doesn't specify voice/silent per command
WA_OPEN_TIMEOUT = 20   # seconds to wait for elements
# -----------------------------------

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

# Initialize TTS
tts_engine = pyttsx3.init()
def speak(text):
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        logging.warning("TTS failed: %s", e)

# ---------- Setup Selenium driver (Brave) ----------
def create_driver():
    options = webdriver.ChromeOptions()
    options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    # Persistent user session (avoids scanning QR every time)
    options.add_argument(r"user-data-dir=C:\Users\User\OneDrive\Desktop\python project self\brave_wa_profile")

    # Safe flags to prevent crashes
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )
    return driver

driver = None
driver_lock = threading.Lock()

def ensure_driver():
    """
    Lazily start the browser for WhatsApp Web if not already started.
    Uses a persistent profile so QR scan is needed only the first time.
    """
    global driver
    with driver_lock:
        if driver is None:
            logging.info("Starting Brave for WhatsApp Web...")
            driver = create_driver()
            driver.get("https://web.whatsapp.com/")
            logging.info("Waiting up to 30s for WhatsApp Web login...")
            start = time.time()
            while True:
                try:
                    # Check for search input to ensure WhatsApp is loaded
                    driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
                    logging.info("WhatsApp Web ready!")
                    break
                except Exception:
                    if time.time() - start > 30:
                        logging.info("If WhatsApp is not logged in, scan QR code in the opened browser.")
                        break
                    time.sleep(1)
        return driver

def remove_non_bmp_chars(text: str):
    """Remove characters outside the Basic Multilingual Plane (e.g., some emojis) to avoid ChromeDriver errors."""
    return ''.join(c for c in text if ord(c) <= 0xFFFF)

# ---------- Helpers ----------

def is_phone_number(s: str) -> bool:
    stripped = re.sub(r"[^\d\+]", "", s)
    # Accept strings with at least 7 digits (change as needed) or starting with +
    digits = re.sub(r"[^\d]", "", stripped)
    return len(digits) >= 7

def normalize_phone(s: str, default_country_code=None):
    # Make E.164-ish naive normalizer: removes spaces/parentheses/dashes.
    s = s.strip()
    s = re.sub(r"[^\d\+]", "", s)
    if s.startswith('+'):
        return s  # assume user provided country code
    digits = re.sub(r"[^\d]", "", s)
    if default_country_code and not digits.startswith(default_country_code):
        return default_country_code + digits
    return digits

# ---------- WhatsApp send logic ----------

def send_whatsapp_direct_number(phone: str, message: str):
    """
    Open direct chat URL for phone and send message via pressing Enter.
    phone: should be digits or +prefixed. message: plain text.
    """
    ensure_driver()
    phone_norm = re.sub(r"[^\d\+]", "", phone)
    # WhatsApp direct url expects phone without '+' and text urlencoded
    phone_for_url = phone_norm.lstrip('+')
    text_for_url = urllib.parse.quote(message)
    url = f"https://web.whatsapp.com/send?phone={phone_for_url}&text={text_for_url}"
    logging.info("Opening URL for direct number: %s", url)
    with driver_lock:
        driver.get(url)
        # wait for chat to load — check for message box
        start = time.time()
        while True:
            try:
                # message input area
                inp = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10' or @data-tab='6' or @data-tab='1']")
                safe_msg = remove_non_bmp_chars(message)
                inp.send_keys(safe_msg)
                time.sleep(0.2)
                inp.send_keys(Keys.ENTER)
                logging.info("Message sent to %s", phone)
                break
            except Exception as e:
                if time.time() - start > 15:
                    logging.error("Failed to send to direct number: %s", e)
                    break
                time.sleep(0.5)

def send_whatsapp_contact_name(name: str, message: str):
    """
    Search for a contact by visible name in WhatsApp and send message.
    """
    ensure_driver()
    logging.info("Searching for contact name: %s", name)
    with driver_lock:
        try:
            # Click the search icon or focus the chat search input
            # New WhatsApp UI: there's a search input with data-tab usually 3
            search_box = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
            search_box.clear()
            time.sleep(0.2)
            search_box.send_keys(name)
            time.sleep(1)  # allow search to populate
            # Click first matching chat
            try:
                first = driver.find_element(By.XPATH, "//div[@role='option'][1]")
                first.click()
            except NoSuchElementException:
                # alternative: search for span that matches name
                elems = driver.find_elements(By.XPATH, f"//span[contains(text(), '{name}')]")
                if elems:
                    elems[0].click()
            time.sleep(0.5)
            # now find message input and send
            inp = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10' or @data-tab='6' or @data-tab='1']")
            safe_msg = remove_non_bmp_chars(message)
            inp.send_keys(safe_msg)
            time.sleep(0.2)
            inp.send_keys(Keys.ENTER)
            logging.info("Message sent to contact: %s", name)
        except Exception as e:
            logging.error("Failed to send to contact name '%s': %s", name, e)

# ---------- Placeholder: Email & SMS ----------

def send_email_stub(recipient_email, message, subject=""):
    logging.info("[EMAIL STUB] Would send email to %s with subject '%s' and message: %s", recipient_email, subject, message)
    # implement SMTP / OAuth as needed

def send_sms_stub(phone, message):
    logging.info("[SMS STUB] Would send SMS to %s with message: %s", phone, message)
    # implement using Twilio or other provider

# ---------- Command parsing & scheduling ----------

def parse_voice_flag(text: str):
    t = text.strip().lower()
    voice = None
    if t.endswith(" voice") or t.endswith(" voice " ) or t.endswith(" voice\n"):
        voice = True
        text = t[:-6].strip()
    elif t.endswith(" silent") or t.endswith(" silent " ) or t.endswith(" silent\n"):
        voice = False
        text = t[:-7].strip()
    return text, voice

def parse_command(natural: str, default_country_code=None):
    """
    Parse strings like:
      send mom in 10 minutes "Pick me up" voice
      message 9841234567 tomorrow 7pm "Hey" silent
      remind me at 5:30pm "Pay the bill"

    Returns a dict:
    {
      platform: "whatsapp"/"email"/"sms",
      recipient_raw: "mom" or "984....",
      message: "...",
      send_at: datetime,
      voice: True/False/None
    }
    """
    original = natural.strip()
    # extract quoted message (prefer " or ')
    msg = ""
    m = re.search(r'["“](.+?)["”]', original)
    if m:
        msg = m.group(1)
        # remove message part from text for parsing the rest
        command_part = original[:m.start()] + original[m.end():]
    else:
        # if no quotes, try last token after time marker by splitting by space from right
        parts = original.split()
        if len(parts) >= 2:
            msg = parts[-1]
            command_part = " ".join(parts[:-1])
        else:
            command_part = original

    # voice flag parsing
    command_part, voice_flag = parse_voice_flag(command_part)

    # determine platform keyword (optional)
    platform = "whatsapp"  # default for now
    lowered = command_part.lower()
    if lowered.startswith("email") or "email" in lowered:
        platform = "email"
    elif lowered.startswith("sms") or lowered.startswith("text") or "sms" in lowered:
        platform = "sms"
    elif lowered.startswith("send") or lowered.startswith("message") or lowered.startswith("remind") or lowered.startswith("tell") or lowered.startswith("text"):
        platform = "whatsapp"

    # find recipient and time phrase: naive split: find first occurrence of ' at ' or ' in ' or ' tomorrow ' or ' today ' or ' on '
    # We'll attempt to extract recipient as the token after the verb
    # Examples:
    # "send mom in 10 minutes"
    # "message 9841234567 tomorrow 7pm"
    # "remind me at 5:30pm"  -> recipient = me
    # Use regex: verb (\S+) (.+time clause...)
    verb_regex = r'^(send|message|remind|tell|text)\s+(.+)$'
    rcpt = None
    time_phrase = None
    remaining = command_part
    mverb = re.search(verb_regex, command_part, flags=re.I)
    if mverb:
        remaining = mverb.group(2).strip()
    # Now remaining may be "mom in 10 minutes" or "984... tomorrow 7pm" or "me at 5pm"
    # Try to find common time indicators and split
    time_indicators = [" in ", " at ", " tomorrow", " tonight", " today", " on ", " next ", " monday", " tuesday", " wednesday", " thursday", " friday", " saturday", " sunday", "am", "pm"]
    split_index = None
    for ind in time_indicators:
        idx = remaining.lower().find(ind)
        if idx != -1:
            split_index = idx
            break
    if split_index is not None:
        rcpt = remaining[:split_index].strip()
        time_phrase = remaining[split_index:].strip()
    else:
        # no indicator found; maybe format "send mom 5pm" or just "send mom"
        tokens = remaining.split(None, 1)
        rcpt = tokens[0].strip()
        time_phrase = tokens[1].strip() if len(tokens) > 1 else ""

    # If recipient is 'me' -> use special handling (send to user's own WhatsApp)
    recipient_raw = rcpt

    # parse time phrase with dateparser
    send_at = None
    if time_phrase:
        # dateparser returns None if fails
        settings = {'PREFER_DATES_FROM': 'future'}
        parsed = dateparser.parse(time_phrase, settings=settings)
        if parsed:
            send_at = parsed
    # if no time found: send immediately
    if not send_at:
        send_at = datetime.now()

    # determine if recipient is phone or name/email
    if platform == "whatsapp":
        if is_phone_number(recipient_raw):
            recipient_type = "phone"
            recipient_value = normalize_phone(recipient_raw, default_country_code=default_country_code)
        else:
            recipient_type = "name"
            recipient_value = recipient_raw
    elif platform == "email":
        recipient_type = "email"
        recipient_value = recipient_raw
    elif platform == "sms":
        recipient_type = "phone"
        recipient_value = normalize_phone(recipient_raw, default_country_code=default_country_code)
    else:
        recipient_type = "unknown"
        recipient_value = recipient_raw

    return {
        "platform": platform,
        "recipient_raw": recipient_raw,
        "recipient_type": recipient_type,
        "recipient": recipient_value,
        "message": msg,
        "send_at": send_at,
        "voice": voice_flag  # may be True/False/None
    }

# ---------- Job scheduling ----------

def schedule_job(cmd: dict):
    """Schedule send job using schedule module (checks every minute)."""
    send_time = cmd["send_at"]
    now = datetime.now()
    if send_time <= now:
        # run immediately
        logging.info("Time is now or past; sending immediately.")
        run_job(cmd)
    else:
        # compute delay in seconds
        delta = (send_time - now).total_seconds()
        logging.info("Scheduling message to %s at %s (in %.0f seconds).", cmd["recipient_raw"], send_time, delta)
        # schedule a lambda in background thread
        threading.Timer(delta, run_job, args=(cmd,)).start()

def run_job(cmd: dict):
    platform = cmd["platform"]
    voice_pref = cmd["voice"]
    if voice_pref is None:
        voice_pref = DEFAULT_VOICE
    # voice: let user hear that job is being executed (before/after)
    if voice_pref:
        speak_text = f"Sending message to {cmd['recipient_raw']} now."
        logging.info("[VOICE] %s", speak_text)
        speak(speak_text)

    if platform == "whatsapp":
        if cmd["recipient_type"] == "phone":
            send_whatsapp_direct_number(cmd["recipient"], cmd["message"])
        else:
            send_whatsapp_contact_name(cmd["recipient"], cmd["message"])
    elif platform == "email":
        send_email_stub(cmd["recipient"], cmd["message"])
    elif platform == "sms":
        send_sms_stub(cmd["recipient"], cmd["message"])
    else:
        logging.warning("Unknown platform for job: %s", platform)

    if voice_pref:
        speak("Message sent.")

# ---------- Simple console UI ----------

def repl_loop(default_country_code=None):
    print("Smart Message Assistant — type 'help' for examples, 'exit' to quit.")
    while True:
        try:
            txt = input("\nEnter command > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        if not txt:
            continue
        if txt.lower() in ("exit", "quit"):
            print("Bye.")
            break
        if txt.lower() in ("help", "?"):
            print_examples()
            continue
        # parse
        cmd = parse_command(txt, default_country_code=default_country_code)
        logging.info("Parsed command: %s", cmd)
        schedule_job(cmd)

def print_examples():
    print("""
Examples:
  send mom in 10 minutes "Pick me up" voice
  message 9841234567 tomorrow 7pm "Hey bro" silent
  remind me at 5:30pm "pay electricity bill"
  email boss tomorrow "Report attached"  (email later)
  text 9801xxxxxx in 2 hours "On my way" voice

Notes:
 - Add 'voice' or 'silent' at the end to override the default for that command.
 - Default behavior is silent unless you specify 'voice'.
 - For phone numbers, include country code if needed: +9198xxxx or 9801xxxx.
""")

# ---------- Start assistant ----------

if __name__ == "__main__":
    print("Starting Smart Message Assistant...")
    print("Default behavior: silent unless you add 'voice' to command.")
    # Optionally, set default country code (e.g., '977' for Nepal). Leave None to not prepend.
    DEFAULT_COUNTRY = None  # e.g., '977' for Nepal if you want to auto-prefix numbers
    # Launch driver lazily when first WhatsApp send is requested.
    repl_loop(default_country_code=DEFAULT_COUNTRY)

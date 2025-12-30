import json
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load env and constants
def find_gemini_files(cache_file=".gemini_cache.json", search_paths=None):
    """
    Finds both:
      - .env file containing Gemini keys
      - token_usage.json file
    Caches paths inside token_usage.json for faster future startup.
    Returns (env_path, json_path)
    """
    target_keywords = ["GEMINI_MAIN_KEY", "GEMINI_"]
    env_path = None
    json_path = None

    # ⚡ Try loading cached paths first
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if isinstance(cached, dict):
                    if cached.get("cached_env_path") and os.path.exists(cached["cached_env_path"]):
                        env_path = cached["cached_env_path"]
                        print(f"⚡ Using cached .env path: {os.path.basename(env_path)}")
                    if cached.get("cached_json_path") and os.path.exists(cached["cached_json_path"]):
                        json_path = cached["cached_json_path"]
                        print(f"⚡ Using cached token_usage.json path: {os.path.basename(json_path)}")
                    if env_path and json_path:
                        return env_path, json_path
        except Exception:
            pass

    # Drives to search
    if search_paths is None:
        drives = [f"{chr(d)}:\\" for d in range(65, 91) if os.path.exists(f"{chr(d)}:\\")]
    else:
        drives = search_paths

    print("🔍 Scanning drives for .env and token_usage.json ...")
    for drive in drives:
        for root, dirs, files in os.walk(drive):
            # Skip system-heavy folders for speed
            if any(skip in root.lower() for skip in ["windows", "program files", "$recycle", "appdata"]):
                continue

            # ✅ Find .env file with Gemini keys
            if not env_path and ".env" in files:
                path = os.path.join(root, ".env")
                try:
                    if os.path.getsize(path) > 2_000_000:
                        continue
                    
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if any(k in content for k in target_keywords):
                            env_path = path
                            print(f"✅ Found Gemini .env at: {env_path}")
                except Exception:
                    pass

            # ✅ Find token_usage.json file
            if not json_path and "token_usage.json" in files:
                json_path = os.path.join(root, "token_usage.json")
                print(f"✅ Found token_usage.json at: {json_path}")

            # Stop when both found
            if env_path and json_path:
                break
        if env_path and json_path:
            break

    # 💾 Cache found paths for next startup
    if env_path or json_path:
        cache_data = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                    if not isinstance(cache_data, dict):
                        cache_data = {}
            except Exception:
                cache_data = {}

        if env_path:
            cache_data["cached_env_path"] = env_path
        if json_path:
            cache_data["cached_json_path"] = json_path

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=4)
        except Exception as e:
            print(f"⚠️ Could not update cache: {e}")

    return env_path, json_path

# Find and load .env and file
env_path, TOKEN_FILE = find_gemini_files()

if env_path:
    load_dotenv(env_path)
    print(f"✅ Loaded .env: {os.path.basename(env_path)}")
else:
    print("⚠️ .env file not found. Using default environment variables.")

# Find and load token_usage.json file
token_data = {}
if TOKEN_FILE and os.path.exists(TOKEN_FILE):
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            token_data = json.load(f)
        print(f"✅ Loaded token_usage.json: {os.path.basename(TOKEN_FILE)}")
    except Exception as e:
        print(f"⚠️ Failed to read token_usage.json: {e}")
else:
    print("⚠️ token_usage.json not found. Will create new one when saving.")

# API keys
DEFAULT_KEYS = [
    {"name": "MAIN", "key": os.getenv("GEMINI_MAIN_KEY"), "tokens_used": 0, "last_request": 0},
    {"name": "BACKUP", "key": os.getenv("GEMINI_MAIN_BACKUP_KEY"), "tokens_used": 0, "last_request": 0},
    {"name": "ALT1", "key": os.getenv("GEMINI_ALT1_KEY"), "tokens_used": 0, "last_request": 0},
    {"name": "ALT2", "key": os.getenv("GEMINI_ALT2_KEY"), "tokens_used": 0, "last_request": 0},
    {"name": "ALT3", "key": os.getenv("GEMINI_ALT3_KEY"), "tokens_used": 0, "last_request": 0},
    {"name": "ALT4", "key": os.getenv("GEMINI_ALT4_KEY"), "total_tokens_used": 0, "last_request": 0},
]

# RPM limits per model
MODEL_RPM = {
    "gemini-2.5-flash": 10,
    "gemini-2.5-flash-lite": 15,
    "gemini-2.0-flash": 15,
    "gemini-2.0-flash-lite": 30,
    "gemini-2.5-pro": 10,
}

# Define models and their practical output tokens limits
MODELS = [
    {"name": "gemini-2.0-flash-lite", "max_output": 400},
    {"name": "gemini-2.0-flash", "max_output": 800},
    {"name": "gemini-2.5-flash-lite", "max_output": 1200},
    {"name": "gemini-2.5-flash", "max_output": 1600},
    {"name": "gemini-2.5-pro", "max_output": 2000},
]

# Load / Save Token Data
def load_token_data():
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                data = json.load(f)
                print("✅ Loaded previous token usage data.")
                return data
        except Exception as e:
            print(f"⚠️ Failed to load token data: {e}, using defaults.")
    return DEFAULT_KEYS

def save_token_data(data):
    try:
        # Make sure each key has name
        for i, key_info in enumerate(data):
            if "name" not in key_info:
                key_info["name"] = DEFAULT_KEYS[i]["name"]
                
        with open(TOKEN_FILE, "w") as f:
            json.dump(data, f, indent=4)
        total_tokens = sum(k.get("tokens_used", 0) for k in data)
        print(f"💾 {TOKEN_FILE} updated at {time.strftime('%Y-%m-%d %H:%M:%S')}. Total tokens used: {total_tokens}")
    except Exception as e:
        print(f"⚠️ Failed to save token data")

API_KEYS = load_token_data()

# Heplers
def select_model(model_token_hint):
    for model in MODELS:
        if model_token_hint <= model["max_output"]:
            return model
    return MODELS[-1]

def wait_for_rpm(key_info, model_name):
    rpm = MODEL_RPM.get(model_name, 15)
    elapsed = time.time() - key_info["last_request"]
    wait_time = max(0, (60 / rpm) - elapsed)
    if wait_time > 0:
        time.sleep(wait_time)

# Gemini Request Function
def ask_gemini(prompt, model_token_hint=400):
    model = select_model(model_token_hint)

    for attempt in range(len(API_KEYS)):
        key_info = API_KEYS[attempt % len(API_KEYS)]
        try:
            wait_for_rpm(key_info, model["name"])

            client = genai.Client(api_key=key_info["key"])
            response = client.models.generate_content(
                model=model["name"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=model["max_output"]
                )
            )

            # Track usage
            key_info["last_request"] = time.time()

            used_tokens = 0
            try:
                used_tokens = response.metadata.usage_metadata.total_token_count
            except AttributeError:
                try:
                    used_tokens = response.usage_metadata.total_token_count
                except AttributeError:
                    print("⚠️ Warning: token_count not available, setting to 50 as fallback")
                    used_tokens = 50

            key_info["tokens_used"] = key_info.get("tokens_used", 0) + used_tokens
            key_info["requests"] = key_info.get("requests", 0) + 1
            key_info["last_request_human"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            save_token_data(API_KEYS)

            return response.text.strip()

        except Exception as e:
            print(f"⚠️ API key '{key_info.get('name','UNKNOWN')}' failed: {e}. Trying next key...")
            continue

    raise RuntimeError("All API keys failed or not valid response received.")


# CLI Interface
if __name__ == "__main__":
    print("🔹 Gemini Prompt Tester 🔹")
    while True:
        user_prompt = input("\nEnter your prompt (or 'exit' to quit): ").strip()
        if user_prompt.lower() == "exit":
            print("\n📊 Final token usage summary:")
            for key_info in API_KEYS:
                print(f"Key {key_info.get('name','UNKNOWN')}: {key_info.get('tokens_used',0)} tokens used")
            save_token_data(API_KEYS)
            print("👋 Exiting and saving token data...")
            break

        try:
            result = ask_gemini(user_prompt)
            print("\n✨ Gemini Response:\n")
            print(result)
        except Exception as e:
            print(f"❌ Error: {e}")

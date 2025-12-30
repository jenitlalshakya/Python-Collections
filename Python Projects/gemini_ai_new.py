import json
import os
import time
import random
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Auto .env and token file detection
def find_gemini_files(cache_file=".gemini_cache.json", search_paths=None):
    target_keywords = ["GEMINI_MAIN_KEY", "GEMINI_"]
    env_path = None
    json_path = None

    #cached paths
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
                env_path = cached.get("cached_env_path")
                json_path = cached.get("cached_json_path")
                if env_path and os.path.exists(env_path):
                    print(f"⚡ Using cached .env path: {os.path.basename(env_path)}")
                if json_path and os.path.exists(json_path):
                    print(f"⚡ Using cached token_usage.json path: {os.path.basename(json_path)}")
                if env_path and json_path:
                    return env_path, json_path
        except Exception:
            pass
    if search_paths is None:
        drives = [f"{chr(d)}:\\" for d in range(65, 91) if os.path.exists(f"{chr(d)}:\\")]
    else:
        drives = search_paths
    
    print("🔍 Scanning drives for .env and token_usage.json ...")
    for drive in drives:
        for root, dirs, files in os.walk(drive):
            if any(skip in root.lower() for skip in ["windows", "progrm files", "$recycle", "appdata"]):
                continue
            if not env_path and ".env" in files:
                path = os.path.join(root, ".env")
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if any(k in content for k in target_keywords):
                            env_path = path
                            print(f"✅ Found .env at: {env_path}")
                except Exception:
                    pass
            if not json_path and "token_usage.json" in files:
                json_path = os.path.join(root, "token_usage.json")
                print(f"✅ Found token_usage.json at: {json_path}")
            if env_path and json_path:
                break
        if env_path and json_path:
            break

    # 💾 cache for next startup
    if env_path or json_path:
        cache_data = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
            except Exception:
                cache_data = {}
        if env_path:
            cache_data["cached_env_path"] = env_path
        if json_path:
            cache_data["cached_json_path"] = json_path
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=4)

    return env_path, json_path

# Load files and config
env_path, TOKEN_FILE = find_gemini_files()

if env_path:
    load_dotenv(env_path)
    print(f"✅ Loaded .env: {os.path.basename(env_path)}")
else:
    print("⚠️ .env file not found. Using system environment variables.")

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

# API Keys + MODEL Config
DEFAULT_KEYS = [
    {"name": "MAIN", "key": os.getenv("GEMINI_MAIN_KEY"), "total_tokens_used": 0, "last_request": 0},
    {"name": "BACKUP", "key": os.getenv("GEMINI_MAIN_BACKUP_KEY"), "total_tokens_used": 0, "last_request": 0},
    {"name": "ALT1", "key": os.getenv("GEMINI_ALT1_KEY"), "total_tokens_used": 0, "last_request": 0},
    {"name": "ALT2", "key": os.getenv("GEMINI_ALT2_KEY"), "total_tokens_used": 0, "last_request": 0},
    {"name": "ALT3", "key": os.getenv("GEMINI_ALT3_KEY"), "total_tokens_used": 0, "last_request": 0},
    {"name": "ALT4", "key": os.getenv("GEMINI_ALT4_KEY"), "total_tokens_used": 0, "last_request": 0},
]

if isinstance(token_data, list):
    existing_names = {k["name"] for k in token_data}
    for d in DEFAULT_KEYS:
        if d["name"] not in existing_names and d["key"]:
            print(f"🆕 Adding new key to token data: {d['name']}")
            token_data.append(d)
    API_KEYS = token_data

MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]

# RPM limits per model
MODEL_RPM = {
    "gemini-2.5-flash": 10,
    "gemini-2.5-flash-lite": 15,
    "gemini-2.0-flash": 15,
    "gemini-2.0-flash-lite": 30,
    "gemini-2.5-pro": 2,
}

#TOKEN DATA Handlers
def save_token_data(data):
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        total_tokens = sum(k.get("total_tokens_used", 0) for k in data)
        print(f"💾 Token data updated. Total tokens used: {total_tokens}")
    except Exception as e:
        print(f"⚠️ Failed to save token data: {e}")

def wait_for_rpm(key_info, model_name):
    rpm = MODEL_RPM.get(model_name, 15)
    elapsed = time.time() - key_info.get("last_request", 0)
    wait_time = max(0, (60 / rpm) - elapsed)
    if wait_time > 0:
        time.sleep(wait_time)

# Smart GEMINI Caller
def ask_gemini(prompt):
    random.shuffle(MODELS)
    for model in MODELS:
        for key_info in API_KEYS:
            api_key = key_info.get("key")
            if not api_key:
                continue

            try:
                wait_for_rpm(key_info, model)
                print(f"⚡ Trying mode: {model} | key: {key_info['name']}")

                client = genai.Client(api_key = api_key)
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                # Track usage
                key_info["last_request"] = time.time()
                used_tokens = 0
                try:
                    used_tokens = response.usage_metadata.total_token_count
                except Exception:
                    used_tokens = 50    #fallback

                # per model tracking
                if "models" not in key_info:
                    key_info["models"] = {}
                if model not in key_info["models"]:
                    key_info["models"][model] = {"tokens_used": 0, "requests": 0}

                key_info["models"][model]["tokens_used"] += used_tokens
                key_info["models"][model]["requests"] += 1

                key_info["total_tokens_used"] = key_info.get("total_tokens_used", 0) + used_tokens
                key_info["requests"] = key_info.get("requests", 0) + 1
                key_info["last_request_human"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                save_token_data(API_KEYS)
                return response.text.strip()

            except Exception as e:
                err = str(e)
                print(f"❌ Error [{model}] [{key_info['name']}]: {err}")

                # Token / rate limit or quota reached
                if any(x in err for x in ["RESOURCE_EXHAUSTED", "429", "Quota", "rate limit"]):
                    print("⏳ Rate / token limit reached - switching key or model...")
                    time.sleep(random.uniform(3, 6))
                    continue

                # Authentication issue
                elif "UNAUTHENTICATED" in err or "API key" in err:
                    print("⚠️ Invalid API key, skipping...")
                    continue

                # Invalid request or model issue
                elif "INVALID_ARGUMENT" in err:
                    print("⚠️ Invalid argument or prompt issue, switching model...")
                    break

                else:
                    print("⚠️ Unknown error, switching...")
    raise RuntimeError("🚫 All models or keys failed. Please try again later.")


# CLI Interface
if __name__ == "__main__":
    while True:
        user_prompt = input("\nEnter your prompt (or 'exit' to quit): ").strip()
        if user_prompt.lower() == "exit":
            print("\n📊 Final usage summary:")
            for k in API_KEYS:
                print(f"• {k.get('name')}: {k.get('total_tokens_used', 0)} tokens, {k.get('requests', 0)} requests")
                if "models" in k:
                    for model_name, m in k["models"].items():
                        print(f"   ↳ {model_name}: {m['tokens_used']} tokens, {m['requests']} requests")
            save_token_data(API_KEYS)
            print("👋 Exiting gracefully...")
            break

        try:
            result = ask_gemini(user_prompt)
            print("\n✨ Gemini Response:\n")
            print(result)
        except Exception as e:
            print(f"❌ Error: {e}")

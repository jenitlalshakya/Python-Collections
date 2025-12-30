import psutil
import json
import os
import time
import datetime

FILE_PATH = os.path.join(os.environ["LOCALAPPDATA"], "usage.json")

def human_bytes(n):
    step = 1024.0
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    value = float(n)
    while value >= step and i < len(units) - 1:
        value /= step
        i += 1
    
    return f"{value:.2f} {units[i]}"

def load_data():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    
    return {"today": 0,
            "yesterday": 0,
            "week": 0,
            "month": 0,
            "last": None,
            "last_day": None,
            "last_week": None,
            "last_month": None
            }

def save_data(d):
    with open(FILE_PATH, "w") as f:
        json.dump(d, f, indent = 4)

def reset_if_needed(d, now):
    day = now.strftime("%Y-%m-%d")
    week = f"{now.year}-W{now.isocalendar()[1]}"
    month = f"{now.year}-{now.month}"

    if d["last_day"] != day:
        d["yesterday"] = d["today"]
        d["today"] = 0
        d["last_day"] = day
    
    if d["last_week"] != week:
        d["week"] = 0
        d["last_week"] = week
    
    if d["last_month"] != month:
        d["month"] = 0
        d["last_month"] = month

def main():
    data = load_data()

    while True:
        now = datetime.datetime.now()
        reset_if_needed(data, now)
        counters = psutil.net_io_counters()
        total = counters.bytes_sent + counters.bytes_recv

        if data["last"] is None:
            data["last"] = total
        
        delta = total-data["last"] if total >= data["last"] else total
        data["last"] = total
        data["today"] += delta
        data["week"] += delta
        data["month"] += delta

        save_data({
            "today": data["today"],
            "yesterday": data["yesterday"],
            "week": data["week"],
            "month": data["month"],
            "last": data["last"],
            "last_day": data["last_day"],
            "last_week": data["last_week"],
            "last_month": data["last_month"],
            "human_readable": {
                "today": human_bytes(data["today"]),
                "yesterday": human_bytes(data["yesterday"]),
                "week": human_bytes(data["week"]),
                "month": human_bytes(data["month"])
            }
        })

        time.sleep(5)

if __name__ == "__main__":
    main()
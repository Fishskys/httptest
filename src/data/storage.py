import os
import json
import datetime
from src.config import LOG_DIR, COLLECTION_FILE


def append_log_to_file(method, url, status):
    """追加日志到文件"""
    try:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        log_file = os.path.join(LOG_DIR, f"{date_str}.log")

        with open(log_file, "a", encoding="utf-8") as f:
            log_line = f"[{time_str}] {status} | {method} {url}\n"
            f.write(log_line)
    except Exception as e:
        print(f"Log Error: {e}")


def load_collections():
    if os.path.exists(COLLECTION_FILE):
        try:
            with open(COLLECTION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []


def save_collections(data_list):
    try:
        with open(COLLECTION_FILE, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=4)
    except Exception as e:
        print(f"Save Collection Error: {e}")

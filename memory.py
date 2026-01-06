import json
import os
from datetime import date

MEMORY_FILE = "user_memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_memory(key, value):
    from datetime import date

def update_memory(key, value):
    data = load_memory()

    today = str(date.today())
    history = data.get("history", [])

    history.append({
        "date": today,
        key: value
    })

    data["history"] = history[-50:]  # ограничим историю
    data[key] = value
    data["last_update"] = today

    save_memory(data)


def get_memory():
    return load_memory()

def set_chat_id(chat_id):
    update_memory("chat_id", chat_id)
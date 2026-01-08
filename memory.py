import json
from datetime import date
from pathlib import Path

FILE = Path("memory.json")

def _load():
    if FILE.exists():
        return json.loads(FILE.read_text())
    return {}

def _save(data):
    FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def update_memory(user_id, key, value):
    data = _load()
    user = data.setdefault(str(user_id), {})
    history = user.setdefault("history", [])

    today = date.today().isoformat()
    entry = next((h for h in history if h["date"] == today), None)

    if not entry:
        entry = {"date": today}
        history.append(entry)

    entry[key] = value
    _save(data)

def get_memory(user_id):
    return _load().get(str(user_id), {})

from memory import get_memory

def daily_summary(user_id):
    m = get_memory(user_id)
    last = m.get("history", [])[-1:] or [{}]
    d = last[0]

    return (
        f"📊 Сегодня:\n"
        f"😴 Сон: {d.get('sleep_hours', '—')}\n"
        f"⚡ Энергия: {d.get('energy_level', '—')}\n"
        f"🏋️ Тренировка: {d.get('last_training', '—')}"
    )

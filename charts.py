import matplotlib.pyplot as plt
from memory import get_memory

def sleep_chart(user_id):
    memory = get_memory(user_id)
    history = memory.get("history", [])

    dates, values = [], []
    for h in history:
        if "sleep_hours" in h:
            dates.append(h["date"])
            values.append(float(h["sleep_hours"]))

    if not values:
        return None

    plt.figure()
    plt.plot(dates, values)
    plt.title("Сон (часы)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = f"sleep_{user_id}.png"
    plt.savefig(path)
    plt.close()
    return path

def energy_chart(user_id):
    memory = get_memory(user_id)
    history = memory.get("history", [])

    dates, values = [], []
    for h in history:
        if "energy_level" in h:
            dates.append(h["date"])
            values.append(int(h["energy_level"]))

    if not values:
        return None

    plt.figure()
    plt.plot(dates, values)
    plt.title("Энергия")
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = f"energy_{user_id}.png"
    plt.savefig(path)
    plt.close()
    return path

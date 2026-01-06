import matplotlib.pyplot as plt
from datetime import date, timedelta
from memory import get_memory


def _last_7_days_data(key):
    memory = get_memory()
    history = memory.get("history", [])

    days = []
    values = []

    week_start = date.today() - timedelta(days=6)

    for item in history:
        try:
            d = date.fromisoformat(item.get("date"))
        except Exception:
            continue

        if d < week_start:
            continue

        if key in item:
            try:
                days.append(d.strftime("%d.%m"))
                values.append(float(item[key]))
            except Exception:
                pass

    return days, values


def sleep_chart():
    days, values = _last_7_days_data("sleep_hours")

    if not values:
        return None

    plt.figure()
    plt.plot(days, values, marker="o")
    plt.title("Сон (часы)")
    plt.xlabel("День")
    plt.ylabel("Часы сна")
    plt.ylim(0, 10)
    plt.grid(True)

    path = "sleep_chart.png"
    plt.savefig(path)
    plt.close()
    return path


def energy_chart():
    days, values = _last_7_days_data("energy_level")

    if not values:
        return None

    plt.figure()
    plt.plot(days, values, marker="o")
    plt.title("Энергия")
    plt.xlabel("День")
    plt.ylabel("Уровень (1–10)")
    plt.ylim(0, 10)
    plt.grid(True)

    path = "energy_chart.png"
    plt.savefig(path)
    plt.close()
    return path
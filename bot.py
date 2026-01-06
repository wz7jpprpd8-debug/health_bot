from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)

from datetime import time, date, timedelta

from config import TELEGRAM_TOKEN
from logic import daily_summary
from ai import ask_ai, analyze_week
from memory import update_memory, get_memory
from charts import sleep_chart, energy_chart


# ──────────────── Клавиатура ────────────────

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🏋️ Тренировка сегодня", callback_data="today_training")],
        [InlineKeyboardButton("🍽 Питание", callback_data="nutrition")],
        [InlineKeyboardButton("😴 Сон", callback_data="sleep_help")],
        [InlineKeyboardButton("📊 Недельный отчёт", callback_data="week_report")],
        [InlineKeyboardButton("📈 Графики", callback_data="charts")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ──────────────── Команды ────────────────

def start(update, context):
    memory = get_memory()
    if not memory.get("chat_id"):
        update_memory("chat_id", update.message.chat_id)

    update.message.reply_text(
        "Привет! Я твой AI-ассистент по здоровью 💪\n\nВыбирай действие:",
        reply_markup=main_keyboard()
    )


def day(update, context):
    update.message.reply_text(daily_summary())


def sleep(update, context):
    if not context.args:
        update.message.reply_text("Используй: /sleep 7")
        return
    update_memory("sleep_hours", context.args[0])
    update.message.reply_text(f"😴 Сон сохранён: {context.args[0]} ч")


def energy(update, context):
    if not context.args:
        update.message.reply_text("Используй: /energy 8")
        return
    update_memory("energy_level", context.args[0])
    update.message.reply_text(f"⚡ Энергия сохранена: {context.args[0]}/10")


def training(update, context):
    if not context.args:
        update.message.reply_text("Используй: /training зал ноги")
        return
    text = " ".join(context.args)
    update_memory("last_training", text)
    update.message.reply_text(f"🏋️ Тренировка записана: {text}")


# ──────────────── AI чат ────────────────

def ai_chat(update, context):
    reply = ask_ai(update.message.text)
    update.message.reply_text(reply)


# ──────────────── Авто-сообщения ────────────────

def morning_job(context):
    chat_id = get_memory().get("chat_id")
    if chat_id:
        context.bot.send_message(
            chat_id=chat_id,
            text="🌅 Доброе утро! Как самочувствие?"
        )


def evening_job(context):
    chat_id = get_memory().get("chat_id")
    if chat_id:
        context.bot.send_message(
            chat_id=chat_id,
            text="🌙 Как прошёл день? Энергия, сон?"
        )


# ──────────────── Отчёт ────────────────

def weekly_report():
    memory = get_memory()
    history = memory.get("history", [])

    if not history:
        return "📊 Недостаточно данных для отчёта"

    week_start = date.today() - timedelta(days=7)
    sleep, energy, trainings = [], [], []

    for item in history:
        try:
            d = date.fromisoformat(item.get("date"))
        except Exception:
            continue

        if d < week_start:
            continue

        if "sleep_hours" in item:
            try:
                sleep.append(float(item["sleep_hours"]))
            except Exception:
                pass

        if "energy_level" in item:
            try:
                energy.append(int(item["energy_level"]))
            except Exception:
                pass

        if "last_training" in item:
            trainings.append(item["last_training"])

    text = "📊 Недельный отчёт\n\n"

    text += f"😴 Сон: {round(sum(sleep)/len(sleep),1) if sleep else 'нет данных'}\n"
    text += f"⚡ Энергия: {round(sum(energy)/len(energy),1) if energy else 'нет данных'}\n"
    text += f"🏋️ Тренировок: {len(trainings)}\n"

    try:
        text += "\n\n🤖 AI-анализ:\n" + analyze_week(text)
    except Exception:
        text += "\n\n🤖 AI-анализ недоступен"

    return text


# ──────────────── Кнопки ────────────────

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    if query.data == "today_training":
        text = ask_ai("Что мне сегодня делать с тренировкой?")
    elif query.data == "nutrition":
        text = ask_ai("Что мне сегодня есть?")
    elif query.data == "sleep_help":
        text = ask_ai("Как улучшить сон сегодня?")
    elif query.data == "week_report":
        text = weekly_report()
    elif query.data == "charts":
        sleep_img = sleep_chart()
        energy_img = energy_chart()

        if sleep_img:
            context.bot.send_photo(chat_id, open(sleep_img, "rb"))
        if energy_img:
            context.bot.send_photo(chat_id, open(energy_img, "rb"))

        context.bot.send_message(chat_id, "Что дальше?", reply_markup=main_keyboard())
        return
    else:
        text = "Неизвестная команда"

    context.bot.send_message(chat_id, text, reply_markup=main_keyboard())


# ──────────────── Запуск ────────────────

def main():
    print("🤖 Бот запускается...")

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("day", day))
    dp.add_handler(CommandHandler("sleep", sleep))
    dp.add_handler(CommandHandler("energy", energy))
    dp.add_handler(CommandHandler("training", training))

    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_chat))

    job_queue = updater.job_queue
    job_queue.run_daily(morning_job, time(hour=8, minute=0))
    job_queue.run_daily(evening_job, time(hour=21, minute=0))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
 
from flask import Flask
import threading
import os

def run_bot():
    main()

def run_server():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "Bot is running"

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_server()
   main()

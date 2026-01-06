from charts import sleep_chart, energy_chart
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)

from datetime import time

from config import TELEGRAM_TOKEN
from logic import daily_summary
from ai import ask_ai
from memory import update_memory, get_memory
from ai import analyze_week


# ──────────────── Команды ────────────────

def start(update, context):
    # сохраняем chat_id
    update_memory("chat_id", update.message.chat_id)

    update.message.reply_text(
        "Привет! Я твой AI-ассистент по здоровью 💪\n\n"
   	 "Выбирай действие:",
   	 reply_markup=main_keyboard())


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


def memory_status(update, context):
    memory = get_memory()
    if not memory:
        update.message.reply_text("Память пока пустая")
    else:
        text = "\n".join([f"{k}: {v}" for k, v in memory.items()])
        update.message.reply_text(f"📊 Текущая память:\n{text}")


# ──────────────── AI чат ────────────────

def ai_chat(update, context):
    reply = ask_ai(update.message.text)
    update.message.reply_text(reply)


# ──────────────── Авто-сообщения ────────────────

def morning_job(update, context):
    memory = get_memory()
    chat_id = memory.get("chat_id")
    if not chat_id:
        return

    context.bot.send_message(
        chat_id=chat_id,
        text="🌅 Доброе утро!\nКак самочувствие? Напиши пару слов — подстрою день 💪"
    )


def evening_job(update, context):
    memory = get_memory()
    chat_id = memory.get("chat_id")
    if not chat_id:
        return

    context.bot.send_message(
        chat_id=chat_id,
        text="🌙 Как прошёл день?\nЭнергия? Во сколько планируешь лечь спать?"
    )


# ──────────────── Запуск ────────────────

def main():
    print("🤖 Бот запускается с AI, памятью и авто-сообщениями...")

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("day", day))
    dp.add_handler(CommandHandler("sleep", sleep))
    dp.add_handler(CommandHandler("energy", energy))
    dp.add_handler(CommandHandler("training", training))

    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_chat))

    updater.start_polling()
    updater.idle()

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🏋️ Тренировка сегодня", callback_data="today_training")],
        [InlineKeyboardButton("🍽 Питание", callback_data="nutrition")],
        [InlineKeyboardButton("😴 Сон", callback_data="sleep_help")],
        [InlineKeyboardButton("📊 Недельный отчёт", callback_data="week_report")],
        [InlineKeyboardButton("📈 Графики", callback_data="charts")],
    ]
    return InlineKeyboardMarkup(keyboard)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

from datetime import date, timedelta

def weekly_report():
    memory = get_memory()
    history = memory.get("history", [])

    if not history:
        return "📊 Недельный отчёт\n\nНедостаточно данных."

    week_start = date.today() - timedelta(days=7)

    sleep = []
    energy = []
    trainings = []

    for item in history:
        try:
            d = date.fromisoformat(item.get("date"))
        except Exception:
            continue

        if d < week_start:
            continue

        # сон
        if "sleep_hours" in item:
            try:
                sleep.append(float(item["sleep_hours"]))
            except Exception:
                pass

        # энергия
        if "energy_level" in item:
            try:
                energy.append(int(item["energy_level"]))
            except Exception:
                pass

        # тренировки
        if "last_training" in item:
            trainings.append(item["last_training"])

    text = "📊 Недельный отчёт\n\n"

    if sleep:
        text += f"😴 Сон: среднее {round(sum(sleep)/len(sleep), 1)} ч\n"
    else:
        text += "😴 Сон: данных мало\n"

    if energy:
        text += f"⚡ Энергия: среднее {round(sum(energy)/len(energy), 1)}/10\n"
    else:
        text += "⚡ Энергия: данных мало\n"

    text += f"🏋️ Тренировок: {len(trainings)}\n\n"

    # вывод
    text += "Вывод:\n"

    if sleep and sum(sleep)/len(sleep) < 7:
        text += "• Сон ниже нормы — стоит снизить нагрузку\n"
    else:
        text += "• Сон в допустимых пределах\n"

    if energy and sum(energy)/len(energy) < 6:
        text += "• Энергия снижена — добавь восстановление\n"
    else:
        text += "• Энергия нормальная\n"

    if len(trainings) < 3:
        text += "• Мало тренировок — верни ритм\n"
    else:
        text += "• Тренировочный ритм нормальный\n"

  # --- AI-анализ недели ---
    try:
        ai_analysis = analyze_week(text)
        text += "\n\n🤖 AI-анализ недели:\n" + ai_analysis
    except Exception:
        text += "\n\n🤖 AI-анализ недоступен"

    return text

def button_handler(update, context):
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id

    if query.data == "today_training":
        text = ask_ai("Что мне сегодня делать с тренировкой?")
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=main_keyboard()
        )

    elif query.data == "nutrition":
        text = ask_ai("Что мне сегодня есть?")
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=main_keyboard()
        )

    elif query.data == "sleep_help":
        text = ask_ai("Как улучшить сон сегодня?")
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=main_keyboard()
        )

    elif query.data == "week_report":
        text = weekly_report()
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=main_keyboard()
        )

    elif query.data == "charts":
        sleep = sleep_chart()
        energy = energy_chart()

        if not sleep and not energy:
            context.bot.send_message(
                chat_id=chat_id,
                text="Недостаточно данных для графиков 📉",
                reply_markup=main_keyboard()
            )
            return

        if sleep:
            with open(sleep, "rb") as f:
                context.bot.send_photo(chat_id=chat_id, photo=f)

        if energy:
            with open(energy, "rb") as f:
                context.bot.send_photo(chat_id=chat_id, photo=f)

    else:
        context.bot.send_message(
            chat_id=chat_id,
            text="Неизвестная кнопка",
            reply_markup=main_keyboard()
        )


if __name__ == "__main__":
    main()

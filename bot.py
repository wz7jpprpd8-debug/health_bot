from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)

from config import TELEGRAM_TOKEN
from memory import update_memory, get_memory
from ai import ask_ai, analyze_week
from charts import sleep_chart, energy_chart
from logic import daily_summary

# ──────────────── КЛАВИАТУРА ────────────────

def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏋️ Тренировка", callback_data="training")],
        [InlineKeyboardButton("🍽 Питание", callback_data="nutrition")],
        [InlineKeyboardButton("😴 Сон", callback_data="sleep_help")],
        [InlineKeyboardButton("📊 Неделя", callback_data="week")],
        [InlineKeyboardButton("📈 Графики", callback_data="charts")],
    ])

# ──────────────── КОМАНДЫ ────────────────

def start(update, context):
    update.message.reply_text(
        "Привет! Я AI-ассистент по здоровью 💪\nВыбирай действие:",
        reply_markup=keyboard()
    )

def sleep(update, context):
    if not context.args:
        update.message.reply_text("Пример: /sleep 7")
        return

    update_memory(update.effective_user.id, "sleep_hours", context.args[0])
    update.message.reply_text("😴 Сон сохранён")

def energy(update, context):
    if not context.args:
        update.message.reply_text("Пример: /energy 8")
        return

    update_memory(update.effective_user.id, "energy_level", context.args[0])
    update.message.reply_text("⚡ Энергия сохранена")

def training(update, context):
    if not context.args:
        update.message.reply_text("Пример: /training зал ноги")
        return

    text = " ".join(context.args)
    update_memory(update.effective_user.id, "last_training", text)
    update.message.reply_text("🏋️ Тренировка записана")

# ──────────────── AI ЧАТ ────────────────

def chat(update, context):
    try:
        reply = ask_ai(update.message.text)
    except Exception:
        reply = "🤖 AI временно недоступен"

    update.message.reply_text(reply)

# ──────────────── КНОПКИ ────────────────

def buttons(update: Update, context):
    q = update.callback_query

    try:
        q.answer()
    except:
        pass  # важно: не падаем, если запрос устарел

    uid = q.from_user.id
    chat_id = q.message.chat_id

    if q.data == "week":
        text = daily_summary(uid)

    elif q.data == "charts":
        s = sleep_chart(uid)
        e = energy_chart(uid)

        if s:
            context.bot.send_photo(chat_id, open(s, "rb"))
        if e:
            context.bot.send_photo(chat_id, open(e, "rb"))

        context.bot.send_message(chat_id, "Что дальше?", reply_markup=keyboard())
        return

    else:
        text = ask_ai("Дай совет по " + q.data)

    context.bot.send_message(chat_id, text, reply_markup=keyboard())

# ──────────────── ЗАПУСК ────────────────

def main():
    print("🤖 Bot started (Railway)")

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("sleep", sleep))
    dp.add_handler(CommandHandler("energy", energy))
    dp.add_handler(CommandHandler("training", training))

    dp.add_handler(CallbackQueryHandler(buttons))  # ← ВАЖНО: ДО MessageHandler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

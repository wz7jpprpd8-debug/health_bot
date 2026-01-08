from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
)
from telegram import Bot

from config import TELEGRAM_TOKEN
from ai import ask_ai
from memory import update_memory, get_memory
from charts import sleep_chart, energy_chart
from logic import daily_summary

import os

# ─────────────────────────────────────────
# BOT + FLASK
# ─────────────────────────────────────────

app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# ─────────────────────────────────────────
# KEYBOARD
# ─────────────────────────────────────────

def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏋️ Тренировка", callback_data="training")],
        [InlineKeyboardButton("🍽 Питание", callback_data="nutrition")],
        [InlineKeyboardButton("😴 Сон", callback_data="sleep")],
        [InlineKeyboardButton("📊 Неделя", callback_data="week")],
        [InlineKeyboardButton("📈 Графики", callback_data="charts")],
    ])

# ─────────────────────────────────────────
# COMMANDS
# ─────────────────────────────────────────

def start(update, context):
    update.message.reply_text(
        "Привет! Я AI-ассистент по здоровью 💪",
        reply_markup=keyboard()
    )

def sleep_cmd(update, context):
    if not context.args:
        update.message.reply_text("Пример: /sleep 7")
        return
    update_memory(update.effective_user.id, "sleep_hours", context.args[0])
    update.message.reply_text("😴 Сон сохранён")

def energy_cmd(update, context):
    if not context.args:
        update.message.reply_text("Пример: /energy 8")
        return
    update_memory(update.effective_user.id, "energy_level", context.args[0])
    update.message.reply_text("⚡ Энергия сохранена")

def training_cmd(update, context):
    text = " ".join(context.args)
    update_memory(update.effective_user.id, "last_training", text)
    update.message.reply_text("🏋️ Тренировка записана")

def chat(update, context):
    update.message.reply_text(ask_ai(update.message.text))

# ─────────────────────────────────────────
# CALLBACK BUTTONS
# ─────────────────────────────────────────

def buttons(update, context):
    q = update.callback_query
    q.answer()
    uid = q.from_user.id

    if q.data == "week":
        text = daily_summary(uid)

    elif q.data == "charts":
        s = sleep_chart(uid)
        e = energy_chart(uid)
        if s:
            context.bot.send_photo(q.message.chat_id, open(s, "rb"))
        if e:
            context.bot.send_photo(q.message.chat_id, open(e, "rb"))
        return

    else:
        text = ask_ai(f"Дай совет по теме: {q.data}")

    context.bot.send_message(
        q.message.chat_id,
        text,
        reply_markup=keyboard()
    )

# ─────────────────────────────────────────
# DISPATCHER
# ─────────────────────────────────────────

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("sleep", sleep_cmd))
dispatcher.add_handler(CommandHandler("energy", energy_cmd))
dispatcher.add_handler(CommandHandler("training", training_cmd))
dispatcher.add_handler(CallbackQueryHandler(buttons))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))

# ─────────────────────────────────────────
# WEBHOOK ENDPOINT
# ─────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Bot is running"

# ─────────────────────────────────────────
# START
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("🤖 Bot started (Webhook mode)")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

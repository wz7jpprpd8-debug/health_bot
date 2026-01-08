import os
from flask import Flask, request

from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)

from config import TELEGRAM_TOKEN
from ai import ask_ai

# ─────────────────────────────────────────
# Flask
# ─────────────────────────────────────────
app = Flask(__name__)

bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)


# ─────────────────────────────────────────
# Keyboard
# ─────────────────────────────────────────
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏋️ Тренировка", callback_data="training")],
        [InlineKeyboardButton("🍽 Питание", callback_data="nutrition")],
        [InlineKeyboardButton("😴 Сон", callback_data="sleep")],
        [InlineKeyboardButton("📊 Неделя", callback_data="week")],
    ])


# ─────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────
def start(update, context):
    update.message.reply_text(
        "🤖 Бот работает!\n\nВыбери действие 👇",
        reply_markup=main_keyboard()
    )


def text_handler(update, context):
    reply = ask_ai(update.message.text)
    update.message.reply_text(reply, reply_markup=main_keyboard())


def buttons(update, context):
    query = update.callback_query

    # ⚠️ важно: отвечаем сразу
    try:
        query.answer()
    except Exception:
        pass

    data = query.data
    chat_id = query.message.chat_id

    if data == "training":
        text = ask_ai("Дай совет по тренировке сегодня")
    elif data == "nutrition":
        text = ask_ai("Что лучше поесть сегодня?")
    elif data == "sleep":
        text = ask_ai("Как улучшить сон сегодня?")
    elif data == "week":
        text = "📊 Недельный отчёт скоро будет здесь"
    else:
        text = "Неизвестная команда"

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=main_keyboard()
    )


# ─────────────────────────────────────────
# Dispatcher
# ─────────────────────────────────────────
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))
dispatcher.add_handler(CallbackQueryHandler(buttons))


# ─────────────────────────────────────────
# Webhook endpoint (ВАЖНО)
# ─────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200


# ─────────────────────────────────────────
# Health check
# ─────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return "Bot is running", 200


# ─────────────────────────────────────────
# Run
# ─────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print("🤖 Bot started (Webhook mode)")
    app.run(host="0.0.0.0", port=port)

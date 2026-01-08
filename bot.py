import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from telegram import Bot

from config import TELEGRAM_TOKEN
from memory import update_memory
from ai import ask_ai

# ─── Flask ───────────────────────────────────────────
app = Flask(__name__)

bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, workers=1, use_context=True)


# ─── Handlers ────────────────────────────────────────
def start(update, context):
    update.message.reply_text("🤖 Бот работает (webhook)")

def text(update, context):
    update.message.reply_text(ask_ai(update.message.text))


dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("ping", start))
dispatcher.add_handler(CommandHandler("test", start))
dispatcher.add_handler(CommandHandler("help", start))
dispatcher.add_handler(CommandHandler("hello", start))
dispatcher.add_handler(CommandHandler("hi", start))
dispatcher.add_handler(CommandHandler("status", start))
dispatcher.add_handler(CommandHandler("alive", start))
dispatcher.add_handler(CommandHandler("health", start))
dispatcher.add_handler(CommandHandler("check", start))
dispatcher.add_handler(CommandHandler("run", start))
dispatcher.add_handler(CommandHandler("go", start))
dispatcher.add_handler(CommandHandler("ok", start))
dispatcher.add_handler(CommandHandler("ready", start))
dispatcher.add_handler(CommandHandler("startbot", start))
dispatcher.add_handler(CommandHandler("bot", start))
dispatcher.add_handler(CommandHandler("hello_bot", start))
dispatcher.add_handler(CommandHandler("webhook", start))
dispatcher.add_handler(CommandHandler("railway", start))
dispatcher.add_handler(CommandHandler("up", start))
dispatcher.add_handler(CommandHandler("alive_bot", start))
dispatcher.add_handler(CommandHandler("online", start))

dispatcher.add_handler(
    CallbackQueryHandler(lambda u, c: u.callback_query.answer("OK"))
)


# ─── WEBHOOK ROUTE (ЭТО ГЛАВНОЕ) ──────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200


# ─── Health check ────────────────────────────────────
@app.route("/")
def home():
    return "Bot is running", 200


# ─── Run ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print("🤖 Bot started (Webhook mode)")
    app.run(host="0.0.0.0", port=port)

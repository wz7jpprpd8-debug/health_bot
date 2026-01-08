from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, CallbackQueryHandler
)

from config import TELEGRAM_TOKEN
from memory import update_memory, get_memory
from ai import ask_ai, analyze_week
from charts import sleep_chart, energy_chart
from logic import daily_summary
from datetime import date, timedelta


def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏋️ Тренировка", callback_data="training")],
        [InlineKeyboardButton("🍽 Питание", callback_data="nutrition")],
        [InlineKeyboardButton("😴 Сон", callback_data="sleep")],
        [InlineKeyboardButton("📊 Неделя", callback_data="week")],
        [InlineKeyboardButton("📈 Графики", callback_data="charts")],
    ])


def start(update, context):
    update.message.reply_text("Привет! Я AI-ассистент 💪", reply_markup=keyboard())


def sleep(update, context):
    if not context.args:
        update.message.reply_text("Пример: /sleep 7")
        return
    update_memory(update.effective_user.id, "sleep_hours", context.args[0])
    update.message.reply_text("Сон сохранён 😴")


def energy(update, context):
    if not context.args:
        update.message.reply_text("Пример: /energy 8")
        return
    update_memory(update.effective_user.id, "energy_level", context.args[0])
    update.message.reply_text("Энергия сохранена ⚡")


def training(update, context):
    text = " ".join(context.args)
    update_memory(update.effective_user.id, "last_training", text)
    update.message.reply_text("Тренировка записана 🏋️")


def chat(update, context):
    update.message.reply_text(ask_ai(update.message.text))


def buttons(update: Update, context):
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
        text = ask_ai("Дай совет по " + q.data)

    context.bot.send_message(q.message.chat_id, text, reply_markup=keyboard())


def main():
    print("🤖 Bot started (Railway)")
    up = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = up.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("sleep", sleep))
    dp.add_handler(CommandHandler("energy", energy))
    dp.add_handler(CommandHandler("training", training))
    dp.add_handler(CallbackQueryHandler(buttons))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))

    up.start_polling()
    up.idle()


if __name__ == "__main__":
    main()

import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN не найден. Проверь .env файл")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY не найден. Проверь .env файл")
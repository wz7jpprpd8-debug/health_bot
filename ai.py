import os
from openai import OpenAI

# ──────────────── НАСТРОЙКИ ────────────────

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

AI_ENABLED = bool(OPENAI_API_KEY)

print("🤖 AI ENABLED:", AI_ENABLED)

if AI_ENABLED:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None


# ──────────────── AI ОТВЕТ ────────────────

def ask_ai(prompt: str) -> str:
    if not AI_ENABLED:
        return "🤖 AI временно отключён"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Ты персональный ассистент по здоровью. Отвечай кратко и по делу."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI ERROR:", e)
        return "🤖 Ошибка AI. Попробуй позже."


# ──────────────── AI АНАЛИЗ НЕДЕЛИ ────────────────

def analyze_week(text: str) -> str:
    if not AI_ENABLED:
        return "AI-анализ отключён"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Ты аналитик здоровья. Дай краткий вывод и рекомендации."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.6,
            max_tokens=250
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI WEEK ERROR:", e)
        return "Не удалось выполнить AI-анализ."

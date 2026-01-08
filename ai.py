print("AI ENABLED:", AI_ENABLED)

import os
from openai import OpenAI
from config import OPENAI_API_KEY

# Флаг: включён ли AI
AI_ENABLED = bool(OPENAI_API_KEY)

# Инициализация клиента (ТОЛЬКО если есть ключ)
client = OpenAI(api_key=OPENAI_API_KEY) if AI_ENABLED else None


def ask_ai(user_text: str) -> str:
    """
    Ответ AI на сообщение пользователя
    """
    if not AI_ENABLED:
        return (
            "🤖 AI временно недоступен.\n\n"
            "Ты можешь пользоваться трекером сна, энергии, тренировок и отчётами."
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты персональный ассистент по здоровью. "
                        "Давай короткие, практичные и мотивирующие советы."
                    )
                },
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=300
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI ERROR:", e)
        return "⚠️ Ошибка AI. Попробуй позже."


def analyze_week(summary_text: str) -> str:
    """
    AI-анализ недельного отчёта
    """
    if not AI_ENABLED:
        return "AI-анализ отключён (нет ключа OpenAI)."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты эксперт по здоровью и восстановлению. "
                        "Проанализируй отчёт и дай рекомендации."
                    )
                },
                {"role": "user", "content": summary_text}
            ],
            temperature=0.6,
            max_tokens=400
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI WEEK ERROR:", e)
        return "⚠️ AI-анализ недели недоступен."

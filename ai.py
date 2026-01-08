import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

AI_ENABLED = bool(OPENAI_API_KEY)
print("🤖 AI ENABLED:", AI_ENABLED)

client = OpenAI(api_key=OPENAI_API_KEY) if AI_ENABLED else None


def ask_ai(prompt: str) -> str:
    if not AI_ENABLED:
        return "⚠️ AI временно отключён"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты персональный AI-ассистент по здоровью."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI ERROR:", e)
        return "⚠️ Ошибка AI"


def analyze_week(text: str) -> str:
    return ask_ai(
        "Проанализируй эту неделю и дай рекомендации:\n\n" + text
    )

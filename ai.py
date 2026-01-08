import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ENABLED = bool(OPENAI_API_KEY)

print("🤖 AI ENABLED:", AI_ENABLED)

_client = None


def get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def ask_ai(prompt: str) -> str:
    if not AI_ENABLED:
        return "AI временно отключён"

    try:
        client = get_client()
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты персональный AI-ассистент по здоровью"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return r.choices[0].message.content.strip()

    except Exception as e:
        return f"AI ошибка: {e}"


def analyze_week(text: str) -> str:
    return ask_ai(
        "Проанализируй неделю пользователя и дай рекомендации:\n\n" + text
    )

from openai import OpenAI
from config import OPENAI_API_KEY
from memory import get_memory

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Ты — персональный AI-ассистент по здоровью, спорту и восстановлению.

СТИЛЬ ОТВЕТА:
- кратко
- по делу
- без мотивационного мусора
- как спокойный опытный тренер 40+

ФОРМАТ ОТВЕТА (ВСЕГДА):
1. Сегодня
2. Почему
3. Что делать

ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
- Мужчина 40+
- Рост 180 см, вес 82 кг
- Зал: 2 раза в неделю
- Эндуро: 1 раз в неделю
- Бег: 3 раза в неделю
- Цель: энергия, форма, здоровье

ПРАВИЛА:
- Не ставь диагнозы
- Не упоминай врачей и лекарства
- Не давай больше 5 пунктов
- Если мало данных — задай 1 уточняющий вопрос в конце
- Всегда давай рекомендацию НА СЕГОДНЯ
"""

def ask_ai(user_text: str) -> str:
    memory = get_memory()

    memory_lines = []
    for key, value in memory.items():
        if key != "chat_id":
            memory_lines.append(f"{key}: {value}")

    memory_block = "\n".join(memory_lines) if memory_lines else "нет данных"

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n\nТекущие данные пользователя:\n" + memory_block
        },
        {
            "role": "user",
            "content": user_text
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()

def analyze_week(stats_text: str) -> str:
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + """
Дополнительно:
Ты анализируешь НЕДЕЛЮ целиком.
Дай:
- 2–3 ключевых вывода
- 3 конкретных рекомендации на следующую неделю
Формат:
Выводы:
• ...
• ...

Рекомендации на следующую неделю:
• ...
• ...
• ...
"""
        },
        {
            "role": "user",
            "content": f"Вот данные за неделю:\n{stats_text}"
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.25,
        max_tokens=350
    )

    return response.choices[0].message.content.strip()

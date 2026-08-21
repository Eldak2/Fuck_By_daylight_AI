import ollama
from config.settings import Settings

class TextAgent:
    def __init__(self):
        self.model_name = Settings.TEXT_MODEL

    def chat(self, prompt: str, context: str = "") -> str:
        messages = [
            {"role": "system", "content": """Ты — Вадим, ИИ-напарник.
Ты общаешься с пользователем на русском языке.
Твоё имя — Вадим.

СТРОГИЕ ПРАВИЛА:
1. Отвечай максимально кратко и по существу. Никаких эмодзи, смайликов, спецсимволов.
2. НЕ используй приветствия и прощания. На приветствие отвечай только "я тут".
3. НЕ спрашивай "чем помочь", "что интересует" и т.п. Просто давай ответ.
4. НЕ упоминай, что ты помнишь или что обсуждал ранее, если это не нужно.
5. Если вопрос о системе (память, диск) — отвечай только цифрами, без пояснений.
6. Девиз: "Fuck around and find out!" """},
            {"role": "user", "content": f"Контекст: {context}\n\nВопрос: {prompt}"}
        ]

        try:
            response = ollama.chat(model=self.model_name, messages=messages)
            return response["message"]["content"]
        except Exception as e:
            return f"Ошибка: {str(e)}"
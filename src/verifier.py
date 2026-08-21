import ollama
import json
import re

def verify_outcome(before_b64: str, after_b64: str, goal: str) -> dict:
    prompt = f"""
    Цель: {goal}
    Сравни два изображения экрана (ДО и ПОСЛЕ выполнения).
    Определи, достигнута ли цель.
    ОТВЕТЬ ТОЛЬКО JSON:
    {{"success": true/false, "message": "краткое описание"}}
    """
    messages = [
        {"role": "system", "content": "Ты — эксперт по верификации."},
        {"role": "user", "content": prompt},
        {"role": "user", "images": [before_b64, after_b64]}
    ]
    try:
        response = ollama.chat(model="qwen2.5-vl:7b", messages=messages)
        text = response["message"]["content"]
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"success": False, "message": "Не удалось распарсить"}
    except Exception:
        return {"success": False, "message": "Ошибка верификации"}
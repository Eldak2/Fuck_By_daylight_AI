import ollama
import json
import re
from typing import Dict, Optional

class GoalPlanner:
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    def create_plan(self, goal: str, context: str = "") -> Optional[Dict]:
        prompt = f"""
        Создай детальный план для: {goal}
        Контекст: {context}
        ОТВЕТЬ ТОЛЬКО JSON:
        {{
            "goal": "{goal}",
            "steps": [
                {{"step": 1, "action": "click", "params": {{"x": 100, "y": 200}}, "description": "Шаг 1"}}
            ],
            "estimated_time": 10
        }}
        """
        messages = [
            {"role": "system", "content": "Ты — планировщик. Только JSON."},
            {"role": "user", "content": prompt}
        ]
        try:
            response = ollama.chat(model=self.model_name, messages=messages)
            text = response["message"]["content"]
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None
        except Exception:
            return None
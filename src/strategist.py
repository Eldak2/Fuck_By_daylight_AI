import ollama
from src.vision import capture_and_prepare_screen
from config.settings import Settings

class Strategist:
    """Анализирует экран через llava:7b"""
    
    def __init__(self):
        self.model_name = Settings.VISION_MODEL
    
    def analyze(self, prompt: str) -> str:
        """Анализирует экран и возвращает ответ на русском"""
        _, b64 = capture_and_prepare_screen()
        
        messages = [
            {"role": "system", "content": "Ты — эксперт по анализу экрана. ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ."},
            {"role": "user", "content": prompt},
            {"role": "user", "images": [b64]}
        ]
        
        try:
            response = ollama.chat(model=self.model_name, messages=messages)
            return response["message"]["content"]
        except Exception as e:
            return f"❌ Ошибка зрения: {str(e)}"
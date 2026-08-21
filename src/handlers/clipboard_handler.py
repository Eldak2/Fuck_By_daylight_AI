import re
import pyperclip
from src.clipboard_image import ClipboardImage

class ClipboardHandler:
    def __init__(self, agent):
        self.agent = agent

    def handle(self, user_goal: str, use_voice: bool) -> str:
        goal_lower = user_goal.lower()
        voice = self.agent.voice

        # Текст
        if "скопируй" in goal_lower or "копировать" in goal_lower:
            text = re.sub(r'скопируй\s*|копировать\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if text:
                pyperclip.copy(text)
                result = "Текст скопирован"
                if use_voice and voice:
                    voice.speak(result)
                return result
            return "Что скопировать?"

        if "покажи буфер" in goal_lower or "что в буфере" in goal_lower:
            content = pyperclip.paste()
            result = f"Буфер: {content[:200]}" if content else "Буфер пуст"
            if use_voice and voice:
                voice.speak(result)
            return result

        # Картинки
        if "скопируй картинку" in goal_lower:
            file_path = re.sub(r'скопируй картинку\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if file_path:
                result = ClipboardImage.copy_image_from_file(file_path)
                if use_voice and voice:
                    voice.speak(result)
                return result
            return "Укажи путь к картинке"

        if "вставь картинку" in goal_lower:
            file_path = re.sub(r'вставь картинку\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if file_path:
                result = ClipboardImage.paste_image_to_file(file_path)
                if use_voice and voice:
                    voice.speak(result)
                return result
            return "Укажи путь для сохранения"

        return None
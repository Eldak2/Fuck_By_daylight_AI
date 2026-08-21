import re
from src.window_manager import WindowManager

class WindowHandler:
    def __init__(self, agent):
        self.agent = agent

    def handle(self, user_goal: str, use_voice: bool) -> str:
        goal_lower = user_goal.lower()
        voice = self.agent.voice

        if "список окон" in goal_lower:
            windows = WindowManager.list_windows()
            if windows:
                result = "Открытые окна:\n" + "\n".join([f"- {w['title']}" for w in windows[:10]])
            else:
                result = "Нет открытых окон"
            if use_voice and voice:
                voice.speak(result)
            return result

        if "закрой окно" in goal_lower:
            title = re.sub(r'закрой окно\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if title:
                result = WindowManager.close_window(title)
                if use_voice and voice:
                    voice.speak(result)
                return result
            return "Укажи название окна"

        if "разверни окно" in goal_lower or "максимизируй окно" in goal_lower:
            title = re.sub(r'разверни окно\s*|максимизируй окно\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if title:
                result = WindowManager.maximize_window(title)
                if use_voice and voice:
                    voice.speak(result)
                return result
            return "Укажи название окна"

        if "сверни окно" in goal_lower or "минимизируй окно" in goal_lower:
            title = re.sub(r'сверни окно\s*|минимизируй окно\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if title:
                result = WindowManager.minimize_window(title)
                if use_voice and voice:
                    voice.speak(result)
                return result
            return "Укажи название окна"

        return None
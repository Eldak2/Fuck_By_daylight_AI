class OverlayHandler:
    def __init__(self, agent):
        self.agent = agent

    def handle(self, user_goal: str, use_voice: bool) -> str:
        goal_lower = user_goal.lower()
        voice = self.agent.voice

        if "включи оверлей" in goal_lower or "выключи оверлей" in goal_lower:
            result = "Функция игрового оверлея временно отключена. Используйте основной оверлей (Ctrl+Shift+G)."
            if use_voice and voice:
                voice.speak(result)
            return result

        return None
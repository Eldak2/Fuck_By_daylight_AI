from src.email_manager import EmailManager

class EmailHandler:
    def __init__(self, agent):
        self.agent = agent
        self.email_manager = EmailManager()

    def handle(self, user_goal: str, use_voice: bool) -> str:
        goal_lower = user_goal.lower()
        voice = self.agent.voice

        if "проверь почту" in goal_lower or "новые письма" in goal_lower:
            result = self.email_manager.get_last_emails()
            if use_voice and voice:
                voice.speak(result[:100])
            return result

        if "отправь письмо" in goal_lower:
            # Простая заглушка – можно реализовать диалог
            return "Для отправки письма используй настройки или скажи подробнее"

        return None
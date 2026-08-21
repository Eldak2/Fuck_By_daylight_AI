import re

class NotificationHandler:
    def __init__(self, agent):
        self.agent = agent

    def handle(self, user_goal: str, use_voice: bool) -> str:
        goal_lower = user_goal.lower()
        voice = self.agent.voice

        if "напомни" in goal_lower:
            match = re.search(r'через\s*(\d+)\s*(сек|мин|ч)', goal_lower)
            if match:
                value = int(match.group(1))
                unit = match.group(2)
                if unit.startswith('сек'):
                    seconds = value
                elif unit.startswith('мин'):
                    seconds = value * 60
                elif unit.startswith('ч'):
                    seconds = value * 3600
                else:
                    seconds = 10
                text = re.sub(r'напомни\s+через\s+\d+\s*(сек|мин|ч)\s*', '', user_goal).strip()
                if text:
                    self.agent.notification_manager.add_reminder(text, seconds)
                    result = f"Напомню через {value} {unit}: {text}"
                    if use_voice and voice:
                        voice.speak(result)
                    return result
            return "Укажи: напомни через 10 мин проверить почту"

        return None
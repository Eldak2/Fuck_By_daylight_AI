from src.updater import Updater

class UpdateHandler:
    def __init__(self, agent):
        self.agent = agent
        self.updater = Updater(agent)

    def check_for_updates(self, background=True):
        self.updater.check_for_updates(background=background)

    def handle(self, user_goal: str, use_voice: bool) -> str:
        goal_lower = user_goal.lower()
        voice = self.agent.voice

        if "проверь обновления" in goal_lower:
            self.updater.check_for_updates(background=False)
            if self.updater.update_available:
                result = "Доступно обновление. Скачать и установить? Скажи 'установить обновление'"
            else:
                result = "Нет обновлений"
            if use_voice and voice:
                voice.speak(result)
            return result

        if "установить обновление" in goal_lower:
            result = self.updater.download_and_install()
            if use_voice and voice:
                voice.speak(result)
            return result

        return None
import re
from datetime import datetime
from src.macro_recorder import MacroRecorder
from src.scheduler import Scheduler

class AutomationHandler:
    def __init__(self, agent):
        self.agent = agent
        self.macro_recorder = MacroRecorder()
        self.scheduler = Scheduler(agent)

    def handle(self, user_goal: str, use_voice: bool) -> str:
        goal_lower = user_goal.lower()
        voice = self.agent.voice

        # Макросы (запись/воспроизведение)
        if "записать макрос" in goal_lower or "начать запись макроса" in goal_lower:
            result = self.macro_recorder.start_recording()
            if use_voice and voice:
                voice.speak(result)
            return result

        if "остановить макрос" in goal_lower or "стоп макрос" in goal_lower:
            result = self.macro_recorder.stop_recording()
            if use_voice and voice:
                voice.speak(result)
            return result

        if "выполнить макрос" in goal_lower or "запустить макрос" in goal_lower:
            result = self.macro_recorder.play_macro()
            if use_voice and voice:
                voice.speak(result)
            return result

        # Планировщик
        if "запланируй" in goal_lower:
            match = re.search(r'в\s*([0-9]{1,2}:[0-9]{2})', goal_lower)
            if match:
                time_str = match.group(1)
                parts = re.split(r'в\s*[0-9]{1,2}:[0-9]{2}', user_goal, maxsplit=1)
                if len(parts) > 1:
                    command = parts[1].strip()
                    self.scheduler.add_task(command, time_str)
                    now = datetime.now().strftime("%H:%M:%S")
                    result = f"Запланировал '{command}' на {time_str} (сейчас {now})"
                    if use_voice and voice:
                        voice.speak(result)
                    return result
            return "Не понял время. Скажи: запланируй в 15:30 скажи привет"

        if "список задач" in goal_lower or "показать задачи" in goal_lower:
            result = self.scheduler.list_tasks()
            if use_voice and voice:
                voice.speak(result)
            return result

        if "очистить задачи" in goal_lower or "удалить задачи" in goal_lower:
            result = self.scheduler.clear_tasks()
            if use_voice and voice:
                voice.speak(result)
            return result

        # Сценарии (управление, список)
        if "список сценариев" in goal_lower:
            if not self.agent.scenarios.scenarios:
                return "Нет активных сценариев"
            result = "Сценарии:\n" + "\n".join([f"{s.name} ({s.condition_type} {s.condition_value} → {s.action_type})" for s in self.agent.scenarios.scenarios if s.enabled])
            if use_voice and voice:
                voice.speak(result[:100])
            return result

        if "выключи сценарий" in goal_lower:
            name = re.sub(r'выключи сценарий\s*', '', user_goal, flags=re.IGNORECASE).strip()
            for s in self.agent.scenarios.scenarios:
                if s.name.lower() == name.lower():
                    s.enabled = False
                    self.agent.scenarios.save()
                    result = f"Сценарий '{name}' отключён"
                    if use_voice and voice:
                        voice.speak(result)
                    return result
            return f"Сценарий '{name}' не найден"

        # Создание сценария – просто перенаправляем в настройки
        if "создай сценарий" in goal_lower:
            return "Используй меню Настройки -> Сценарии для создания"

        return None
import schedule
import time
import threading
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, agent):
        self.agent = agent
        self.running = False
        self.thread = None
        self.tasks = []

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Планировщик задач запущен")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Планировщик остановлен")

    def _run_loop(self):
        while self.running:
            try:
                schedule.run_pending()
            except Exception as e:
                logger.error(f"Ошибка в планировщике: {e}")
            time.sleep(0.5)  # увеличили точность

    def add_task(self, command: str, time_str: str, day: str = None):
        """
        Добавляет задачу. Если время уже прошло, выполнит сразу.
        """
        try:
            now = datetime.now()
            target_time = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            # Если время уже прошло сегодня — выполняем сразу
            if target_time < now:
                logger.warning(f"Время {time_str} уже прошло. Выполняю задачу немедленно: {command}")
                self._execute(command)
                return True

            if day:
                getattr(schedule.every(), day).at(time_str).do(self._execute, command)
            else:
                schedule.every().day.at(time_str).do(self._execute, command)

            self.tasks.append({"command": command, "time": time_str, "day": day})
            logger.info(f"Задача добавлена: '{command}' в {time_str}" + (f" (каждый {day})" if day else ""))
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления задачи: {e}")
            return False

    def _execute(self, command):
        try:
            logger.info(f"Выполняю задачу: '{command}' в {datetime.now().strftime('%H:%M:%S')}")
            self.agent.think_and_act(command, use_voice=False)
        except Exception as e:
            logger.error(f"Ошибка выполнения задачи '{command}': {e}")

    def list_tasks(self):
        if not self.tasks:
            return "Нет запланированных задач"
        result = []
        for t in self.tasks:
            day_str = f" (каждый {t['day']})" if t['day'] else " (ежедневно)"
            result.append(f"- {t['command']} в {t['time']}{day_str}")
        return "\n".join(result)

    def clear_tasks(self):
        schedule.clear()
        self.tasks.clear()
        logger.info("Все задачи удалены")
        return "Все задачи удалены"
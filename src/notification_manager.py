import threading
import time
import logging
from src.settings_manager import SettingsManager

logger = logging.getLogger(__name__)
settings = SettingsManager()

class NotificationManager:
    def __init__(self, agent):
        self.agent = agent
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        if not settings.get("notifications_enabled"):
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("NotificationManager started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _loop(self):
        import psutil
        while self.running:
            try:
                battery = psutil.sensors_battery()
                if battery and battery.percent < 20 and not battery.power_plugged:
                    msg = f"⚠️ Заряд батареи: {battery.percent}% (подключи зарядку!)"
                    self.agent.add_notification(msg)
                time.sleep(60)
            except Exception as e:
                logger.error(f"Notification error: {e}")
                time.sleep(60)

    def add_reminder(self, text, seconds):
        def reminder():
            time.sleep(seconds)
            self.agent.add_notification(f"🔔 Напоминание: {text}")
        threading.Thread(target=reminder, daemon=True).start()
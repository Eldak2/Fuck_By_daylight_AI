import threading
import time
import logging

logger = logging.getLogger(__name__)

class AutoMode:
    def __init__(self, agent, interval: int = 30):
        self.agent = agent
        self.interval = interval
        self.running = False
        self.thread = None
    
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("🤖 Автономный режим запущен")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("⏹️ Автономный режим остановлен")
    
    def _run_loop(self):
        while self.running:
            try:
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Ошибка: {e}")
                time.sleep(5)
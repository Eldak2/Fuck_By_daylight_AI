import os
import sys
import time
import signal
import logging
from pathlib import Path

class DaemonService:
    def __init__(self, agent):
        self.agent = agent
        self.running = True
        self.pid_file = Path("agent.pid")
        self.log_file = Path("logs/daemon.log")
        self.log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        try:
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
        except AttributeError:
            pass
    
    def start(self):
        if self.pid_file.exists():
            with open(self.pid_file, 'r') as f:
                old_pid = int(f.read())
                if self._is_process_running(old_pid):
                    print(f"⚠️ Демон уже запущен (PID: {old_pid})")
                    return
        
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        self.logger.info("🤖 Демон запущен")
        self._run_loop()
    
    def _run_loop(self):
        print("🤖 Демон запущен. Работаю в фоне...")
        while self.running:
            try:
                time.sleep(60)
            except Exception as e:
                self.logger.error(f"Ошибка: {e}")
                time.sleep(10)
        if self.pid_file.exists():
            self.pid_file.unlink()
        self.logger.info("🛑 Демон остановлен")
    
    def signal_handler(self, signum, frame):
        print("\n🛑 Остановка...")
        self.running = False
        sys.exit(0)
    
    def _is_process_running(self, pid):
        try:
            import psutil
            return psutil.pid_exists(pid)
        except:
            return False
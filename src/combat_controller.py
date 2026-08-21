import threading
import time
import logging
from src.vision import capture_screen
from src.combat_client import CombatVLA_Client
from src.actions import execute_action_safe
import pyautogui

logger = logging.getLogger(__name__)

class CombatController:
    def __init__(self, agent):
        self.agent = agent
        self.client = CombatVLA_Client()
        self.running = False
        self.thread = None
        self.fps = 2

    def start(self):
        if self.running:
            return
        if not self.client.check_health():
            logger.warning("CombatVLA сервер не доступен")
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("⚔️ Боевой режим CombatVLA активирован")
        self.agent.add_notification("⚔️ Боевой режим включён")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("⏹️ Боевой режим CombatVLA остановлен")
        self.agent.add_notification("⏹️ Боевой режим выключен")

    def _loop(self):
        while self.running:
            try:
                img = capture_screen()
                img.thumbnail((640, 480))
                response = self.client.predict_action(img)
                if "action" in response:
                    self._execute_action(response["action"])
                else:
                    logger.warning(f"Неизвестный ответ: {response}")
                time.sleep(1.0 / self.fps)
            except Exception as e:
                logger.error(f"Ошибка в цикле CombatVLA: {e}")
                time.sleep(0.5)

    def _execute_action(self, action_str: str):
        if not action_str or action_str.startswith("ERROR"):
            return
        action_lower = action_str.lower().strip()
        if action_lower.startswith("press "):
            key = action_lower.replace("press ", "").strip()
            pyautogui.press(key)
        elif action_lower.startswith("click "):
            parts = action_lower.replace("click ", "").split()
            if len(parts) >= 2:
                try:
                    x, y = int(parts[0]), int(parts[1])
                    pyautogui.click(x, y)
                except:
                    pass
        elif "move" in action_lower:
            pass
        else:
            logger.debug(f"Неизвестное действие: {action_str}")
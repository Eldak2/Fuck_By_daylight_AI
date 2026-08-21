import subprocess
import threading
import time
from typing import Dict, List

class Tactician:
    """Быстрый тактик. Реагирует на угрозы, уклоняется, дерётся."""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or "models/combatvla.pt"
        self.running = False
        self.thread = None
        self.current_action = {"type": "idle"}
    
    def start_combat_mode(self):
        """Запускает боевой режим в фоне"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._combat_loop)
        self.thread.daemon = True
        self.thread.start()
        print("⚔️ Боевой режим активирован")
    
    def stop_combat_mode(self):
        """Останавливает боевой режим"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("⚔️ Боевой режим деактивирован")
    
    def _combat_loop(self):
        """Цикл обработки боевых ситуаций"""
        while self.running:
            try:
                from src.vision import capture_and_prepare_screen
                _, b64 = capture_and_prepare_screen()
                
                threat = self._detect_threat(b64)
                if threat:
                    self._react_to_threat(threat)
                
                time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ Ошибка тактика: {e}")
                time.sleep(0.5)
    
    def _detect_threat(self, screen_b64: str) -> Dict:
        """Определяет, есть ли враги или опасность"""
        return None
    
    def _react_to_threat(self, threat: Dict):
        """Реагирует на угрозу"""
        from src.actions import execute_action_safe
        
        if threat.get("type") == "zombie":
            execute_action_safe({"type": "press", "key": "space"})
            execute_action_safe({"type": "press", "key": "shift"})
        elif threat.get("type") == "fall":
            execute_action_safe({"type": "press", "key": "ctrl"})
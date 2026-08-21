import pyautogui
import keyboard
import time
import json
import threading
import logging

logger = logging.getLogger(__name__)

class MacroRecorder:
    def __init__(self):
        self.actions = []
        self.recording = False
        self.thread = None

    def start_recording(self):
        if self.recording:
            return "⏺️ Уже записываю"
        self.actions = []
        self.recording = True
        self.thread = threading.Thread(target=self._record_loop)
        self.thread.daemon = True
        self.thread.start()
        return "🔴 Запись макроса начата (нажми F12 для остановки)"

    def stop_recording(self):
        self.recording = False
        if self.thread:
            self.thread.join(timeout=2)
        return f"⏹️ Запись остановлена ({len(self.actions)} действий)"

    def _record_loop(self):
        keyboard.add_hotkey('f12', lambda: setattr(self, 'recording', False))
        while self.recording:
            # Запись кликов и клавиш
            event = keyboard.read_event(suppress=False)
            if event.event_type == 'down':
                self.actions.append({
                    "type": "key",
                    "key": event.name,
                    "time": time.time()
                })
            # Здесь можно добавить запись мыши через pyautogui (сложнее)

    def save_macro(self, filename="macro.json"):
        with open(filename, 'w') as f:
            json.dump(self.actions, f, indent=2)
        return f"💾 Макрос сохранён в {filename}"

    def load_macro(self, filename="macro.json"):
        with open(filename, 'r') as f:
            self.actions = json.load(f)
        return f"📂 Макрос загружен ({len(self.actions)} действий)"

    def play_macro(self, speed=1.0):
        for action in self.actions:
            if action["type"] == "key":
                pyautogui.press(action["key"])
                time.sleep(0.05 / speed)
        return "▶️ Макрос выполнен"
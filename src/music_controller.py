import pyautogui
import subprocess
import logging

logger = logging.getLogger(__name__)

class MusicController:
    @staticmethod
    def play_pause():
        pyautogui.press("playpause")
        return "▶️ Play/Pause"

    @staticmethod
    def next_track():
        pyautogui.press("nexttrack")
        return "⏭️ Следующий трек"

    @staticmethod
    def prev_track():
        pyautogui.press("prevtrack")
        return "⏮️ Предыдущий трек"

    @staticmethod
    def volume_up():
        pyautogui.press("volumeup")
        return "🔊 Громкость +"

    @staticmethod
    def volume_down():
        pyautogui.press("volumedown")
        return "🔉 Громкость -"

    @staticmethod
    def mute():
        pyautogui.press("volumemute")
        return "🔇 Звук выключен"

    @staticmethod
    def open_player(app_name: str = "spotify"):
        try:
            subprocess.Popen(app_name)
            return f"🎵 Открыл {app_name}"
        except:
            return f"❌ Не удалось открыть {app_name}"
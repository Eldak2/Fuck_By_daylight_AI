import pygetwindow as gw
import pyautogui
import logging

logger = logging.getLogger(__name__)

class WindowManager:
    @staticmethod
    def list_windows():
        windows = gw.getAllWindows()
        result = []
        for w in windows:
            if w.title:
                result.append({
                    "title": w.title,
                    "x": w.left,
                    "y": w.top,
                    "width": w.width,
                    "height": w.height,
                    "is_minimized": w.isMinimized,
                    "is_maximized": w.isMaximized
                })
        return result

    @staticmethod
    def close_window(title_part: str):
        for w in gw.getWindowsWithTitle(title_part):
            w.close()
            logger.info(f"✅ Закрыто окно: {w.title}")
            return f"Закрыл окно: {w.title}"
        return f"❌ Окно с '{title_part}' не найдено"

    @staticmethod
    def minimize_window(title_part: str):
        for w in gw.getWindowsWithTitle(title_part):
            w.minimize()
            return f"Свернул окно: {w.title}"
        return f"❌ Окно с '{title_part}' не найдено"

    @staticmethod
    def maximize_window(title_part: str):
        for w in gw.getWindowsWithTitle(title_part):
            w.maximize()
            return f"Развернул окно: {w.title}"
        return f"❌ Окно с '{title_part}' не найдено"

    @staticmethod
    def move_window(title_part: str, x: int, y: int):
        for w in gw.getWindowsWithTitle(title_part):
            w.moveTo(x, y)
            return f"Переместил окно '{w.title}' в ({x}, {y})"
        return f"❌ Окно с '{title_part}' не найдено"
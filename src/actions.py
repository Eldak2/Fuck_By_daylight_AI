import pyautogui
import time
import logging

logger = logging.getLogger(__name__)
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

def validate_coordinates(x: int, y: int) -> bool:
    width, height = pyautogui.size()
    return 0 <= x <= width and 0 <= y <= height

def execute_action_safe(action: dict) -> str:
    action_type = action.get("type", "").lower()
    
    try:
        if action_type == "click":
            x, y = action.get("x"), action.get("y")
            if not validate_coordinates(x, y):
                return f"❌ Координаты ({x}, {y}) вне экрана"
            button = action.get("button", "left")
            clicks = action.get("clicks", 1)
            pyautogui.click(x, y, clicks=clicks, button=button)
            return f"✅ Клик в ({x}, {y})"
            
        elif action_type == "type":
            text = action.get("text", "")
            if text:
                pyautogui.write(text)
                return f"✅ Введён текст: {text[:50]}..."
            return "❌ Нет текста для ввода"
            
        elif action_type == "press":
            key = action.get("key", "")
            if key:
                pyautogui.press(key)
                return f"✅ Нажата клавиша: {key}"
            return "❌ Нет клавиши для нажатия"
            
        elif action_type == "hotkey":
            keys = action.get("keys", [])
            if keys:
                pyautogui.hotkey(*keys)
                return f"✅ Нажата комбинация: {', '.join(keys)}"
            return "❌ Нет клавиш для комбинации"
            
        elif action_type == "scroll":
            amount = action.get("amount", 0)
            pyautogui.scroll(amount)
            return f"✅ Скролл на {amount}"
            
        elif action_type == "move":
            x, y = action.get("x"), action.get("y")
            duration = action.get("duration", 0.3)
            if validate_coordinates(x, y):
                pyautogui.moveTo(x, y, duration=duration)
                return f"✅ Перемещение в ({x}, {y})"
            return f"❌ Координаты ({x}, {y}) вне экрана"
            
        elif action_type == "wait":
            seconds = action.get("seconds", 1)
            time.sleep(seconds)
            return f"✅ Ожидание {seconds} секунд"
            
        else:
            return f"❌ Неизвестное действие: {action_type}"
            
    except pyautogui.FailSafeException:
        return "⛔ Аварийная остановка (FAILSAFE)"
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return f"❌ Ошибка: {str(e)}"
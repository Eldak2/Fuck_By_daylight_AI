import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication
from src.overlay_ui import OverlayWindow

# ===== ГЛОБАЛЬНЫЙ ПЕРЕХВАТЧИК ОШИБОК =====
def global_exception_handler(exc_type, exc_value, exc_tb):
    """Записывает все необработанные исключения в crash.log"""
    with open("crash.log", "a", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"Тип: {exc_type.__name__}\n")
        f.write(f"Значение: {exc_value}\n")
        f.write("".join(traceback.format_tb(exc_tb)))
        f.write("=" * 60 + "\n\n")
    # Выводим в консоль (если она есть)
    print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {exc_value}\n")
    traceback.print_exception(exc_type, exc_value, exc_tb)
    # Не завершаем программу принудительно, пусть окно продолжит работу если возможно
    # но если это критично, можно вызвать sys.exit(1)

sys.excepthook = global_exception_handler

def run_overlay():
    app = QApplication(sys.argv)
    window = OverlayWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_overlay()
from PIL import ImageGrab, Image
import pyperclip
import io
import os

class ClipboardImage:
    @staticmethod
    def copy_image_from_file(file_path: str) -> str:
        try:
            img = Image.open(file_path)
            output = io.BytesIO()
            img.save(output, format="PNG")
            data = output.getvalue()
            pyperclip.copy(data)  # не работает для изображений
            # Альтернатива: используем win32clipboard
            import win32clipboard
            from io import BytesIO
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return f"Изображение скопировано: {os.path.basename(file_path)}"
        except Exception as e:
            return f"Ошибка копирования изображения: {e}"

    @staticmethod
    def paste_image_to_file(file_path: str) -> str:
        try:
            import win32clipboard
            from PIL import Image
            win32clipboard.OpenClipboard()
            try:
                data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
            except:
                return "В буфере нет изображения"
            win32clipboard.CloseClipboard()
            img = Image.open(io.BytesIO(data))
            img.save(file_path)
            return f"Изображение вставлено в: {file_path}"
        except Exception as e:
            return f"Ошибка вставки изображения: {e}"
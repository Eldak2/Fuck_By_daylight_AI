import mss
from PIL import Image
import io
import base64

def capture_screen(monitor_number: int = 1):
    with mss.mss() as sct:
        monitor = sct.monitors[monitor_number]
        screenshot = sct.grab(monitor)
        return Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)

def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def resize_image(image: Image.Image, max_size: int = 1024) -> Image.Image:
    if max(image.size) <= max_size:
        return image
    ratio = max_size / max(image.size)
    new_size = tuple(int(dim * ratio) for dim in image.size)
    return image.resize(new_size, Image.Resampling.LANCZOS)

def capture_and_prepare_screen():
    img = capture_screen()
    resized = resize_image(img)
    b64 = image_to_base64(resized)
    return resized, b64
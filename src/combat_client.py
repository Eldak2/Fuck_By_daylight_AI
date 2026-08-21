import requests
import base64
import io
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class CombatVLA_Client:
    def __init__(self, api_url="http://127.0.0.1:8000"):
        self.api_url = api_url

    def check_health(self):
        try:
            r = requests.get(f"{self.api_url}/health", timeout=2)
            return r.status_code == 200
        except:
            return False

    def predict_action(self, image: Image.Image, prompt: str = "What should I do next in this game? Give concise action.") -> dict:
        if not self.check_health():
            return {"action": "idle", "error": "CombatVLA не отвечает"}
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()
        try:
            r = requests.post(
                f"{self.api_url}/predict",
                json={"image": img_b64, "prompt": prompt},
                timeout=2.0
            )
            if r.status_code == 200:
                return r.json()
            else:
                return {"action": "idle", "error": f"Ошибка {r.status_code}"}
        except Exception as e:
            logger.error(f"Ошибка CombatVLA: {e}")
            return {"action": "idle", "error": str(e)}
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "Fuck_By_Daylight_AI"
    PROJECT_VERSION = "2.0.0"

    # Модели
    TEXT_MODEL = os.getenv("TEXT_MODEL", "qwen2.5:7b")
    VISION_MODEL = os.getenv("VISION_MODEL", "llava:7b")

    # Настройки
    SAFE_MODE = os.getenv("SAFE_MODE", "true").lower() == "true"
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    ACTION_TIMEOUT = int(os.getenv("ACTION_TIMEOUT", 10))
    PAUSE_SECONDS = float(os.getenv("PAUSE_SECONDS", 0.2))
    MAX_HISTORY_TOKENS = int(os.getenv("MAX_HISTORY_TOKENS", 4096))
    LTM_COLLECTION = os.getenv("LTM_COLLECTION", "agent_memory")
    VOICE_LANG = os.getenv("VOICE_LANG", "ru-RU")
    VOICE_SPEED = int(os.getenv("VOICE_SPEED", 150))
    AUTO_MODE_INTERVAL = int(os.getenv("AUTO_MODE_INTERVAL", 30))
    TURBO_MODE = os.getenv("TURBO_MODE", "false").lower() == "true"
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
import json
import os
from src.settings_manager import SettingsManager

settings = SettingsManager()

TRANSLATIONS = {
    "ru": {
        "hello": "Привет! Я Вадим, твой AI-напарник.",
        "menu": "Меню",
        "settings": "Настройки",
        "online": "Онлайн",
        "offline": "Офлайн",
        "language": "Язык",
        "tts_voice": "Голос TTS",
        "tts_rate": "Скорость речи",
        "tts_volume": "Громкость",
        "email_config": "Настройки почты",
        "email_username": "Логин",
        "email_password": "Пароль",
        "notifications": "Уведомления",
        "game_overlay": "Игровой оверлей",
        "save": "Сохранить",
    },
    "en": {
        "hello": "Hello! I'm Vadim, your AI assistant.",
        "menu": "Menu",
        "settings": "Settings",
        "online": "Online",
        "offline": "Offline",
        "language": "Language",
        "tts_voice": "TTS Voice",
        "tts_rate": "Speech Rate",
        "tts_volume": "Volume",
        "email_config": "Email Settings",
        "email_username": "Username",
        "email_password": "Password",
        "notifications": "Notifications",
        "game_overlay": "Game Overlay",
        "save": "Save",
    }
}

class LangManager:
    def __init__(self):
        self.current_lang = settings.get("language", "ru")

    def tr(self, key):
        return TRANSLATIONS.get(self.current_lang, {}).get(key, key)

    def set_language(self, lang):
        if lang in TRANSLATIONS:
            self.current_lang = lang
            settings.set("language", lang)

    def get_languages(self):
        return list(TRANSLATIONS.keys())
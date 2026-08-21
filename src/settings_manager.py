import json
import os

SETTINGS_FILE = "settings.json"

class SettingsManager:
    _defaults = {
        "language": "ru",
        "tts_voice": "default",
        "tts_rate": 150,
        "tts_volume": 0.9,
        "email_smtp_server": "smtp.gmail.com",
        "email_smtp_port": 587,
        "email_imap_server": "imap.gmail.com",
        "email_username": "",
        "email_password": "",
        "notifications_enabled": True,
        "game_overlay_enabled": False,
        "game_overlay_position": "top-right"
    }

    def __init__(self):
        self.data = self._load()

    def _load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    return {**self._defaults, **json.load(f)}
            except:
                pass
        return self._defaults.copy()

    def save(self):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
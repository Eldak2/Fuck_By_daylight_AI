import requests
import os
import zipfile
import json
import shutil
import subprocess
import sys
import threading
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# GitHub репозиторий для проверки версий (можешь заменить на свой)
GITHUB_REPO = "aleks/Fuck_By_Daylight_AI"  # твой username/репо
RELEASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
VERSION_FILE = "version.json"
CURRENT_VERSION = "2.0.0"  # версия агента

class Updater:
    def __init__(self, agent):
        self.agent = agent
        self.update_available = False
        self.downloaded_file = None

    def check_for_updates(self, background=True):
        def check():
            try:
                resp = requests.get(RELEASE_URL, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    latest_version = data.get("tag_name", "").lstrip('v')
                    if latest_version > CURRENT_VERSION:
                        self.update_available = True
                        self.download_url = data.get("assets", [{}])[0].get("browser_download_url")
                        logger.info(f"Новая версия: {latest_version}")
                        if not background:
                            self.agent.add_notification(f"🔔 Доступна новая версия {latest_version}")
                    else:
                        logger.info("Нет обновлений")
                else:
                    logger.warning("Не удалось проверить обновления")
            except Exception as e:
                logger.error(f"Ошибка проверки обновлений: {e}")
        threading.Thread(target=check, daemon=True).start()

    def download_and_install(self):
        if not self.update_available or not self.download_url:
            return "Нет доступных обновлений"
        try:
            self.agent.add_notification("⏬ Скачивание обновления...")
            resp = requests.get(self.download_url, stream=True)
            zip_path = "update.zip"
            with open(zip_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            # Распаковка
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("update_temp")
            self.agent.add_notification("📦 Установка обновления...")
            # Замена файлов (кроме папок config, logs, chroma_db, avatars)
            for root, dirs, files in os.walk("update_temp"):
                for file in files:
                    src = os.path.join(root, file)
                    dst = os.path.join(".", os.path.relpath(src, "update_temp"))
                    if not dst.startswith(("config/", "logs/", "chroma_db/", "avatars/", "settings.json", "config.json")):
                        shutil.copy2(src, dst)
            # Очистка
            os.remove(zip_path)
            shutil.rmtree("update_temp")
            self.update_available = False
            self.agent.add_notification("✅ Обновление установлено. Перезапусти агент.")
            return "Обновление установлено. Перезапусти."
        except Exception as e:
            return f"Ошибка обновления: {e}"
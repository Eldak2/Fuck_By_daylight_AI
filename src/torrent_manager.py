import subprocess
import re
import logging
import requests
import os

logger = logging.getLogger(__name__)

class TorrentManager:
    def __init__(self):
        self.client = None
        self._detect_client()

    def _detect_client(self):
        # Проверяем наличие qBittorrent (через Web API)
        try:
            r = requests.get("http://localhost:8080/api/v2/app/version", timeout=2)
            if r.status_code == 200:
                self.client = "qbittorrent"
                self.qb_url = "http://localhost:8080"
                self.qb_username = "admin"
                self.qb_password = "adminadmin"  # стандартный пароль
                self._qb_login()
                logger.info("qBittorrent найден")
                return
        except:
            pass

        # Проверяем Transmission (через командную строку)
        try:
            subprocess.run(["transmission-remote", "--help"], capture_output=True, check=True)
            self.client = "transmission"
            logger.info("Transmission найден")
            return
        except:
            pass

        # Если ничего не найдено
        self.client = None
        logger.warning("Торрент-клиент не найден")

    def _qb_login(self):
        try:
            s = requests.Session()
            s.post(f"{self.qb_url}/api/v2/auth/login",
                   data={"username": self.qb_username, "password": self.qb_password})
            self.qb_session = s
        except:
            pass

    def add_torrent(self, magnet_or_path: str) -> str:
        if not self.client:
            return "Торрент-клиент не найден"
        if self.client == "qbittorrent":
            try:
                if magnet_or_path.startswith("magnet:"):
                    self.qb_session.post(f"{self.qb_url}/api/v2/torrents/add",
                                          data={"urls": magnet_or_path})
                    return "Торрент добавлен"
                else:
                    # file upload not implemented for simplicity
                    return "Для .torrent файлов пока не реализовано"
            except Exception as e:
                return f"Ошибка добавления: {e}"
        elif self.client == "transmission":
            try:
                subprocess.run(["transmission-remote", "-a", magnet_or_path], check=True)
                return "Торрент добавлен"
            except Exception as e:
                return f"Ошибка добавления: {e}"
        return "Неизвестный клиент"

    def list_torrents(self) -> str:
        if not self.client:
            return "Торрент-клиент не найден"
        if self.client == "qbittorrent":
            try:
                resp = self.qb_session.get(f"{self.qb_url}/api/v2/torrents/info")
                data = resp.json()
                if not data:
                    return "Нет активных торрентов"
                result = []
                for t in data:
                    name = t.get("name", "Без имени")
                    progress = t.get("progress", 0) * 100
                    status = "Активен" if t.get("state") != "paused" else "Приостановлен"
                    result.append(f"{name} - {progress:.1f}% ({status})")
                return "\n".join(result)
            except Exception as e:
                return f"Ошибка получения списка: {e}"
        elif self.client == "transmission":
            try:
                out = subprocess.check_output(["transmission-remote", "-l"], text=True)
                return out
            except Exception as e:
                return f"Ошибка: {e}"
        return "Неизвестный клиент"

    def remove_torrent(self, name: str) -> str:
        if not self.client:
            return "Торрент-клиент не найден"
        if self.client == "qbittorrent":
            try:
                resp = self.qb_session.get(f"{self.qb_url}/api/v2/torrents/info")
                data = resp.json()
                hashes = [t["hash"] for t in data if name.lower() in t["name"].lower()]
                if not hashes:
                    return f"Не найден торрент: {name}"
                for h in hashes:
                    self.qb_session.post(f"{self.qb_url}/api/v2/torrents/delete",
                                         data={"hashes": h, "deleteFiles": "false"})
                return f"Торрент(ы) удалён: {name}"
            except Exception as e:
                return f"Ошибка удаления: {e}"
        elif self.client == "transmission":
            try:
                out = subprocess.check_output(["transmission-remote", "-l"], text=True)
                # Находим ID по имени
                for line in out.splitlines():
                    if name.lower() in line.lower():
                        parts = line.split()
                        if parts:
                            torrent_id = parts[0].strip()
                            if torrent_id.isdigit():
                                subprocess.run(["transmission-remote", "-t", torrent_id, "--remove"], check=True)
                                return f"Торрент удалён: {name}"
                return f"Не найден торрент: {name}"
            except Exception as e:
                return f"Ошибка удаления: {e}"
        return "Неизвестный клиент"
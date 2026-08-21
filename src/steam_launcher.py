import subprocess
import os
import json
import re
import logging

logger = logging.getLogger(__name__)

class SteamLauncher:
    def __init__(self):
        self.steam_path = self._find_steam()
        self.library_folders = self._get_library_folders()

    def _find_steam(self):
        possible_paths = [
            "C:\\Program Files (x86)\\Steam\\steam.exe",
            "C:\\Program Files\\Steam\\steam.exe",
            os.path.expanduser("~") + "\\AppData\\Local\\Steam\\steam.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def _get_library_folders(self):
        if not self.steam_path:
            return []
        # Читаем libraryfolders.vdf
        steam_dir = os.path.dirname(self.steam_path)
        vdf_path = os.path.join(steam_dir, "steamapps", "libraryfolders.vdf")
        if not os.path.exists(vdf_path):
            return [os.path.join(steam_dir, "steamapps")]
        folders = []
        with open(vdf_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Парсим пути
            matches = re.findall(r'"path"\s*"([^"]+)"', content)
            for m in matches:
                # Убираем двойные обратные слеши
                path = m.replace("\\\\", "\\")
                if os.path.exists(os.path.join(path, "steamapps")):
                    folders.append(os.path.join(path, "steamapps"))
        if not folders:
            folders.append(os.path.join(steam_dir, "steamapps"))
        return folders

    def find_game_appid(self, game_name: str) -> str:
        # Ищем в библиотеке папки .acf файлы
        for folder in self.library_folders:
            if not os.path.exists(folder):
                continue
            for file in os.listdir(folder):
                if file.endswith(".acf"):
                    acf_path = os.path.join(folder, file)
                    try:
                        with open(acf_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            # Ищем имя игры
                            name_match = re.search(r'"name"\s*"([^"]+)"', content)
                            if name_match and game_name.lower() in name_match.group(1).lower():
                                # Находим appid
                                appid_match = re.search(r'"appid"\s*"(\d+)"', content)
                                if appid_match:
                                    return appid_match.group(1)
                    except:
                        pass
        return None

    def launch_game(self, game_name: str) -> str:
        if not self.steam_path:
            return "Steam не найден"
        appid = self.find_game_appid(game_name)
        if appid:
            try:
                subprocess.Popen([self.steam_path, f"steam://rungameid/{appid}"])
                return f"Запускаю игру: {game_name}"
            except Exception as e:
                return f"Ошибка запуска: {e}"
        else:
            # Попробуем поискать через steam://store/ и открыть страницу
            return f"Игра '{game_name}' не найдена в библиотеке. Попробуй поискать в Steam."
import subprocess
import os
import shutil
import re
from difflib import get_close_matches

class AppHandler:
    def __init__(self, agent):
        self.agent = agent

    def handle(self, user_goal: str, use_voice: bool) -> str:
        goal_lower = user_goal.lower()
        voice = self.agent.voice

        # Открытие приложений
        open_words = ["открой", "запусти", "открыть", "запустить"]
        if any(word in goal_lower for word in open_words):
            app_name = user_goal
            for word in open_words:
                if word in goal_lower:
                    app_name = user_goal.lower().replace(word, "").strip()
                    break
            if not app_name:
                return "Укажи название приложения"
            try:
                result = self._open_application(app_name)
                if use_voice and voice:
                    voice.speak(result)
                return result
            except Exception as e:
                return f"Ошибка при открытии '{app_name}': {e}"

        # Запуск игр через Steam
        if "запусти игру" in goal_lower or ("игра" in goal_lower and "steam" not in goal_lower):
            game_name = re.sub(r'запусти игру\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if game_name:
                result = self.agent.steam.launch_game(game_name)
                if use_voice and voice:
                    voice.speak(result)
                return result
            return "Укажи название игры"

        return None

    def _open_application(self, app_name: str) -> str:
        # код из старого agent.py
        app_name = app_name.strip().lower()
        popular_apps = {
            "steam": "steam.exe",
            "стим": "steam.exe",
            "паровоз": "steam.exe",
            "dying light": "steam.exe",
            "dying": "steam.exe",
            "dark souls": "steam.exe",
            "chrome": "chrome.exe",
            "хром": "chrome.exe",
            "гугл": "chrome.exe",
            "браузер": "chrome.exe",
            "firefox": "firefox.exe",
            "лиса": "firefox.exe",
            "опера": "opera.exe",
            "brave": "brave.exe",
            "word": "winword.exe",
            "ворд": "winword.exe",
            "excel": "excel.exe",
            "эксель": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "презентация": "powerpnt.exe",
            "outlook": "outlook.exe",
            "почта": "outlook.exe",
            "проводник": "explorer.exe",
            "explorer": "explorer.exe",
            "панель управления": "control.exe",
            "control": "control.exe",
            "диспетчер задач": "taskmgr.exe",
            "task manager": "taskmgr.exe",
            "калькулятор": "calc.exe",
            "calc": "calc.exe",
            "терминал": "wt.exe",
            "cmd": "cmd.exe",
            "командная строка": "cmd.exe",
            "powershell": "powershell.exe",
            "power shell": "powershell.exe",
            "discord": "discord.exe",
            "дискорд": "discord.exe",
            "телеграм": "telegram.exe",
            "telegram": "telegram.exe",
            "тг": "telegram.exe",
            "whatsapp": "whatsapp.exe",
            "вацап": "whatsapp.exe",
            "vscode": "code.exe",
            "visual studio code": "code.exe",
            "код": "code.exe",
            "среда": "code.exe",
            "pycharm": "pycharm64.exe",
            "пичарм": "pycharm64.exe",
            "winrar": "winrar.exe",
            "архиватор": "winrar.exe",
            "7zip": "7zFM.exe",
            "семь зип": "7zFM.exe",
            "плеер": "wmplayer.exe",
            "музыка": "wmplayer.exe",
            "видео": "wmplayer.exe",
            "фото": "photos.exe",
            "фотографии": "photos.exe",
            "snapchat": "snapchat.exe",
            "скриншот": "snippingtool.exe",
            "ножницы": "snippingtool.exe",
        }
        if app_name in popular_apps:
            try:
                subprocess.Popen(popular_apps[app_name], shell=True)
                return f"Открыл {app_name}"
            except Exception as e:
                pass

        all_app_keys = list(popular_apps.keys())
        close_matches = get_close_matches(app_name, all_app_keys, n=1, cutoff=0.6)
        if close_matches:
            best_match = close_matches[0]
            try:
                subprocess.Popen(popular_apps[best_match], shell=True)
                return f"Открыл {best_match} (похоже на '{app_name}')"
            except:
                pass

        exe_path = self._find_exe_in_system(app_name)
        if exe_path:
            try:
                subprocess.Popen(exe_path, shell=True)
                return f"Открыл {os.path.basename(exe_path)} (найден в системе)"
            except:
                pass

        try:
            subprocess.Popen(["start", app_name], shell=True)
            return f"Открыл {app_name} (через start)"
        except:
            pass

        exe_path = shutil.which(app_name + ".exe")
        if exe_path:
            try:
                subprocess.Popen(exe_path, shell=True)
                return f"Открыл {app_name} (найден в PATH)"
            except:
                pass

        return f"Не удалось открыть '{app_name}'. Проверь название или установку."

    def _find_exe_in_system(self, app_name: str):
        app_name_lower = app_name.lower()
        common_paths = [
            "C:\\Program Files\\",
            "C:\\Program Files (x86)\\",
            os.path.expanduser("~") + "\\AppData\\Local\\",
            os.path.expanduser("~") + "\\AppData\\Roaming\\",
        ]
        found_exes = []
        for path in common_paths:
            if not os.path.exists(path):
                continue
            try:
                for root, dirs, files in os.walk(path):
                    try:
                        for file in files:
                            if file.lower().endswith(".exe"):
                                file_name_no_ext = os.path.splitext(file)[0].lower()
                                if app_name_lower in file_name_no_ext or file_name_no_ext in app_name_lower:
                                    found_exes.append(os.path.join(root, file))
                                elif get_close_matches(app_name_lower, [file_name_no_ext], n=1, cutoff=0.7):
                                    found_exes.append(os.path.join(root, file))
                    except PermissionError:
                        continue
                    except Exception:
                        continue
            except Exception:
                continue
        if found_exes:
            return found_exes[0]
        return None
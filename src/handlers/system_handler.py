import os
import subprocess
import psutil
import re
from src.hardware_monitor import HardwareMonitor
from src.system_monitor import SystemMonitor

class SystemHandler:
    def __init__(self, agent):
        self.agent = agent

    def handle(self, user_goal: str, use_voice: bool) -> str:
        goal_lower = user_goal.lower()
        voice = self.agent.voice

        # Статистика системы
        system_keywords = ["диск", "память", "процессор", "свободно", "загруженность",
                           "осталось", "место", "свободное", "занято", "объём", "гигабайт"]
        if any(word in goal_lower for word in system_keywords):
            try:
                stats = SystemMonitor.get_stats()
                result = (f"CPU: {stats['cpu']}%\n"
                          f"RAM: {stats['ram_used']:.1f} ГБ из {stats['ram_total']:.1f} ГБ ({stats['ram_percent']}%)\n"
                          f"Диск: свободно {stats['disk_total'] - stats['disk_used']:.1f} ГБ из {stats['disk_total']:.1f} ГБ")
                alerts = SystemMonitor.alert_if_high()
                if alerts:
                    result += "\n" + "\n".join(alerts)
                if use_voice and voice:
                    voice.speak(result)
                return result
            except Exception as e:
                return f"Не удалось получить статистику системы: {e}"

        # Температура
        if "температура" in goal_lower or "нагрев" in goal_lower:
            cpu_temp = HardwareMonitor.get_cpu_temperature()
            gpu_temp = HardwareMonitor.get_gpu_temperature()
            result = ""
            if cpu_temp is not None:
                result += f"CPU: {cpu_temp}°C"
            else:
                result += "CPU: нет данных"
            if gpu_temp is not None:
                result += f", GPU: {gpu_temp}°C"
            if not result:
                result = "Не удалось получить температуру"
            if use_voice and voice:
                voice.speak(result)
            return result

        # Процессы
        if "список процессов" in goal_lower or "процессы" in goal_lower:
            procs = []
            for proc in psutil.process_iter(['name', 'pid', 'cpu_percent', 'memory_info']):
                try:
                    procs.append(f"{proc.info['name']} (PID: {proc.info['pid']}, CPU: {proc.info['cpu_percent']}%, RAM: {proc.info['memory_info'].rss // 1024 // 1024} MB)")
                except:
                    pass
            result = "\n".join(procs[:20]) if procs else "Нет процессов"
            if use_voice and voice:
                voice.speak("Показаны 20 процессов")
            return result

        if "закрой процесс" in goal_lower or "убей процесс" in goal_lower:
            name = re.sub(r'закрой процесс\s*|убей процесс\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if name:
                killed = False
                for proc in psutil.process_iter(['name', 'pid']):
                    try:
                        if proc.info['name'] and name.lower() in proc.info['name'].lower():
                            proc.kill()
                            killed = True
                            result = f"Завершён процесс {proc.info['name']} (PID: {proc.info['pid']})"
                            if use_voice and voice:
                                voice.speak(result)
                            return result
                    except:
                        pass
                result = f"Не найден процесс с именем {name}"
                if use_voice and voice:
                    voice.speak(result)
                return result
            return "Укажи имя процесса"

        # Управление питанием и Windows
        if "выключи пк" in goal_lower or "выключи компьютер" in goal_lower:
            if use_voice and voice:
                voice.speak("Точно выключить компьютер? Скажи да или нет")
            os.system("shutdown /s /t 10")
            result = "Выключение через 10 секунд"
            if use_voice and voice:
                voice.speak(result)
            return result

        if "перезагрузи пк" in goal_lower or "перезагрузи компьютер" in goal_lower:
            if use_voice and voice:
                voice.speak("Точно перезагрузить компьютер? Скажи да или нет")
            os.system("shutdown /r /t 10")
            result = "Перезагрузка через 10 секунд"
            if use_voice and voice:
                voice.speak(result)
            return result

        if "спящий режим" in goal_lower or "усыпи" in goal_lower:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            result = "ПК переведён в спящий режим"
            if use_voice and voice:
                voice.speak(result)
            return result

        if "гибернация" in goal_lower:
            os.system("shutdown /h")
            result = "ПК переведён в гибернацию"
            if use_voice and voice:
                voice.speak(result)
            return result

        if "заблокируй экран" in goal_lower:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            result = "Экран заблокирован"
            if use_voice and voice:
                voice.speak(result)
            return result

        if "режим не беспокоить" in goal_lower:
            if "включи" in goal_lower:
                os.system("powershell -Command \"Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings' -Name 'NOC_GLOBAL_SETTING_TOASTS_ENABLED' -Value 0\"")
                result = "Режим не беспокоить включён"
            else:
                os.system("powershell -Command \"Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings' -Name 'NOC_GLOBAL_SETTING_TOASTS_ENABLED' -Value 1\"")
                result = "Режим не беспокоить выключен"
            if use_voice and voice:
                voice.speak(result)
            return result

        if "выключи монитор" in goal_lower:
            os.system("powershell -Command \"(Add-Type '[DllImport(\\\"user32.dll\\\")]public static extern int SendMessage(int hWnd, int hMsg, int wParam, int lParam);' -Name a -Pas)::SendMessage(0xffff, 0x0112, 0xF170, 2)\"")
            result = "Монитор выключен"
            if use_voice and voice:
                voice.speak(result)
            return result

        # Открытие папок и команды (тоже системные)
        if "открой папку" in goal_lower:
            path = re.sub(r'открой папку\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if path:
                try:
                    os.startfile(path)
                    result = f"Открыл папку {path}"
                except:
                    result = f"Не удалось открыть папку {path}"
                if use_voice and voice:
                    voice.speak(result)
                return result
            return "Укажи путь к папке"

        if "выполни команду" in goal_lower:
            cmd = re.sub(r'выполни команду\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if cmd:
                try:
                    output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
                    result = output[:500] if output else "Команда выполнена без вывода"
                except subprocess.CalledProcessError as e:
                    result = f"Ошибка: {e.output}"
                if use_voice and voice:
                    voice.speak("Команда выполнена")
                return result
            return "Укажи команду"

        if "админ команда" in goal_lower:
            cmd = re.sub(r'админ команда\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if cmd:
                try:
                    subprocess.Popen(f"runas /user:Administrator \"{cmd}\"", shell=True)
                    result = "Запущена команда от администратора (требуется подтверждение UAC)"
                except:
                    result = "Ошибка запуска от администратора"
                if use_voice and voice:
                    voice.speak("Запуск команды от администратора")
                return result
            return "Укажи команду"

        return None
import re
from src.registry_manager import RegistryManager

class RegistryHandler:
    def __init__(self, agent):
        self.agent = agent
        self.reg = RegistryManager()

    def handle(self, user_goal: str, use_voice: bool) -> str:
        goal_lower = user_goal.lower()
        voice = self.agent.voice

        if "прочитай реестр" in goal_lower:
            path = re.sub(r'прочитай реестр\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if path:
                result = self.reg.read_key(path)
                if use_voice and voice:
                    voice.speak(result[:100])
                return result
            return "Укажи путь в реестре"

        if "запиши в реестр" in goal_lower:
            match = re.search(r'(.+?)\s+значение\s*=\s*([^\s]+)', user_goal, re.IGNORECASE)
            if match:
                path = match.group(1).strip()
                value_data = match.group(2).strip()
                if "\\" in path:
                    path_parts = path.split("\\")
                    if len(path_parts) > 1:
                        value_name = path_parts.pop()
                        subkey_path = "\\".join(path_parts)
                        result = self.reg.write_key(subkey_path, value_name, value_data)
                        if use_voice and voice:
                            voice.speak(result)
                        return result
            return "Неверный формат: запиши в реестр HKEY...\ключ значение = данные"

        if "удали из реестра" in goal_lower:
            path = re.sub(r'удали из реестра\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if path:
                if use_voice and voice:
                    voice.speak("Точно удалить ключ реестра? Скажи да или нет")
                result = self.reg.delete_key(path)
                if use_voice and voice:
                    voice.speak(result)
                return result
            return "Укажи путь"

        return None
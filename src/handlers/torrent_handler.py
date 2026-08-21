import re
from src.torrent_manager import TorrentManager

class TorrentHandler:
    def __init__(self, agent):
        self.agent = agent
        self.torrent = TorrentManager()

    def handle(self, user_goal: str, use_voice: bool) -> str:
        goal_lower = user_goal.lower()
        voice = self.agent.voice

        if "добавь торрент" in goal_lower or "торрент добавить" in goal_lower:
            magnet = re.sub(r'добавь торрент\s*|торрент добавить\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if magnet:
                result = self.torrent.add_torrent(magnet)
                if use_voice and voice:
                    voice.speak(result)
                return result
            return "Укажи magnet-ссылку"

        if "список торрентов" in goal_lower or "торренты" in goal_lower:
            result = self.torrent.list_torrents()
            if use_voice and voice:
                voice.speak(result[:100])
            return result

        if "удали торрент" in goal_lower:
            name = re.sub(r'удали торрент\s*', '', user_goal, flags=re.IGNORECASE).strip()
            if name:
                result = self.torrent.remove_torrent(name)
                if use_voice and voice:
                    voice.speak(result)
                return result
            return "Укажи имя торрента"

        return None
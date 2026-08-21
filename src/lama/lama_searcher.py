import psutil
import requests
import logging
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)

class LamaSearcher:
    def __init__(self, knowledge):
        self.knowledge = knowledge
        self.game_processes = {
            "Dying Light 2": ["DyingLightGame.exe", "DyingLight2.exe"],
            "Cyberpunk 2077": ["Cyberpunk2077.exe"],
            "The Witcher 3": ["witcher3.exe"],
            "Elden Ring": ["eldenring.exe"],
            "Red Dead Redemption 2": ["RDR2.exe"],
            "Black Myth Wukong": ["b1-Win64-Shipping.exe", "Wukong.exe"],
            "Counter-Strike 2": ["cs2.exe"],
            "Dota 2": ["dota2.exe"],
            "League of Legends": ["League of Legends.exe"],
            "Minecraft": ["javaw.exe"],
            "Valorant": ["VALORANT.exe"],
            "Apex Legends": ["r5apex.exe"],
            "Warframe": ["Warframe.x64.exe"],
            "GTA V": ["GTA5.exe"],
            "World of Warcraft": ["Wow.exe"],
        }
        self.cached_game = None

    def detect_game(self):
        """Определяет текущий активный игровой процесс"""
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                for game, exes in self.game_processes.items():
                    if name in exes:
                        return game
            except:
                pass
        return None

    def fetch_game_info(self, game_name):
        """Ищет информацию об игре в интернете (один раз, потом кэширует)"""
        if not game_name:
            return None

        # Проверяем, есть ли уже в памяти
        if self.knowledge.get_all_facts(game_name):
            return self.knowledge.get_all_facts(game_name)

        # Ищем в интернете
        try:
            # Короткая выдержка из Википедии или другого источника
            query = game_name.replace(" ", "+")
            url = f"https://ru.wikipedia.org/wiki/{query}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Ищем первый абзац
                p = soup.find('p')
                if p:
                    description = p.text.strip()[:300]
                    self.knowledge.add_fact(game_name, "description", description)
                    return self.knowledge.get_all_facts(game_name)
        except:
            pass

        # Если интернет недоступен или ничего не найдено, используем заглушку
        self.knowledge.add_fact(game_name, "description", "Информация об игре недоступна.")
        return self.knowledge.get_all_facts(game_name)

    def update_knowledge(self):
        """Обновляет базу знаний, если игра активна"""
        game = self.detect_game()
        if game and game != self.cached_game:
            self.cached_game = game
            info = self.fetch_game_info(game)
            if info:
                logger.info(f"Получена информация об игре {game}: {list(info.keys())}")
            return game
        return None
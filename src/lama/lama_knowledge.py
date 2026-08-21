import json
import os
import logging

logger = logging.getLogger(__name__)

class LamaKnowledge:
    def __init__(self, data_dir="src/lama/lama_data"):
        self.data_dir = data_dir
        self.knowledge_file = os.path.join(data_dir, "knowledge.json")
        self.knowledge = {}
        self._ensure_dir()
        self._load()

    def _ensure_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

    def _load(self):
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    self.knowledge = json.load(f)
            except:
                self.knowledge = {}
        else:
            self.knowledge = {}

    def _save(self):
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)

    def add_fact(self, game_name, key, value):
        if game_name not in self.knowledge:
            self.knowledge[game_name] = {}
        self.knowledge[game_name][key] = value
        self._save()

    def get_fact(self, game_name, key):
        return self.knowledge.get(game_name, {}).get(key, None)

    def get_all_facts(self, game_name):
        return self.knowledge.get(game_name, {})

    def add_info(self, game_name, info_dict):
        if game_name not in self.knowledge:
            self.knowledge[game_name] = {}
        self.knowledge[game_name].update(info_dict)
        self._save()

    def get_game_summary(self, game_name):
        facts = self.get_all_facts(game_name)
        if not facts:
            return "Ничего не известно об этой игре."
        lines = [f"🎮 {game_name}"]
        for k, v in facts.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)
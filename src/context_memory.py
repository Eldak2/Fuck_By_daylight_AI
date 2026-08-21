import json
import os
from collections import deque
from typing import List, Dict, Optional

class ContextMemory:
    """
    Умная память, которая запоминает ТОЛЬКО важное.
    - Хранит последние 20 сообщений для контекста
    - Сохраняет факты о пользователе
    - Старые сообщения сжимает в выжимку
    """
    
    def __init__(self, memory_file="context_memory.json"):
        self.memory_file = memory_file
        self.last_messages = deque(maxlen=20)  # Только последние 20 сообщений
        self.facts = {}  # Важные факты о пользователе
        self.conversation_summary = ""  # Краткая выжимка всего диалога
        
        self._load()
    
    def add_message(self, role: str, content: str):
        """Добавляет сообщение в контекст"""
        self.last_messages.append({"role": role, "content": content})
        
        # Если накопилось много сообщений — обновляем выжимку
        if len(self.last_messages) >= 20:
            self._update_summary()
        
        self._save()
    
    def add_fact(self, key: str, value: str):
        """Сохраняет важный факт о пользователе"""
        self.facts[key] = value
        self._save()
    
    def get_context(self) -> str:
        """Возвращает контекст для модели"""
        context = []
        
        # Факты о пользователе
        if self.facts:
            facts_str = "\n".join([f"{k}: {v}" for k, v in self.facts.items()])
            context.append(f"📋 Факты о пользователе:\n{facts_str}")
        
        # Выжимка диалога
        if self.conversation_summary:
            context.append(f"📝 Суть прошлых разговоров:\n{self.conversation_summary}")
        
        # Последние сообщения
        if self.last_messages:
            messages_str = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in self.last_messages
            ])
            context.append(f"💬 Последние сообщения:\n{messages_str}")
        
        return "\n\n".join(context)
    
    def _update_summary(self):
        """Обновляет выжимку диалога (сжимает старые сообщения)"""
        summary = []
        for msg in list(self.last_messages)[:-5]:  # Все, кроме последних 5
            if len(msg['content']) > 50:
                summary.append(f"{msg['role']}: {msg['content'][:50]}...")
            else:
                summary.append(f"{msg['role']}: {msg['content']}")
        
        self.conversation_summary = "\n".join(summary[-10:])  # Храним только последние 10 строк выжимки
        
        # Оставляем только последние 5 сообщений (остальное в выжимке)
        self.last_messages = deque(list(self.last_messages)[-5:], maxlen=20)
    
    def _save(self):
        """Сохраняет память в файл"""
        data = {
            "facts": self.facts,
            "conversation_summary": self.conversation_summary,
            "last_messages": list(self.last_messages)
        }
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения памяти: {e}")
    
    def _load(self):
        """Загружает память из файла"""
        if not os.path.exists(self.memory_file):
            return
        
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.facts = data.get("facts", {})
                self.conversation_summary = data.get("conversation_summary", "")
                self.last_messages = deque(
                    data.get("last_messages", []),
                    maxlen=20
                )
        except Exception as e:
            print(f"⚠️ Ошибка загрузки памяти: {e}")
    
    def clear(self):
        """Очищает память"""
        self.facts = {}
        self.last_messages.clear()
        self.conversation_summary = ""
        self._save()
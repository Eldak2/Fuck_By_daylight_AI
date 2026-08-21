from typing import List, Dict

class ShortTermMemory:
    def __init__(self, max_tokens: int = 4096):
        self.history = []
        self.max_tokens = max_tokens
        self.system_prompt = ""
        self.token_count = 0
    
    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt
    
    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        self.token_count += len(content) // 4
        while self.token_count > self.max_tokens and self.history:
            removed = self.history.pop(0)
            self.token_count -= len(removed["content"]) // 4
    
    def get_context(self) -> List[Dict]:
        context = []
        if self.system_prompt:
            context.append({"role": "system", "content": self.system_prompt})
        context.extend(self.history)
        return context
    
    def clear(self):
        self.history = []
        self.token_count = 0
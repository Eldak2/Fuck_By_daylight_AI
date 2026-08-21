import re
import threading
import time
from src.voice import VoiceInterface

class WakeWordDetector:
    def __init__(self, agent, wake_word=["вадим"]):
        if isinstance(wake_word, str):
            wake_word = [wake_word]
        self.wake_words = [w.lower() for w in wake_word]
        self.agent = agent
        self.is_active = False
        self.is_running = False
        self.thread = None
        self.voice = VoiceInterface()
        self.last_command = ""

    def start_listening(self):
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._listen_loop)
        self.thread.daemon = True
        self.thread.start()
        print("[INFO] Слушаю... Скажи 'Вадим' или 'Окей, Гугл' для активации")

    def stop_listening(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("[INFO] Прослушивание остановлено")

    def _listen_loop(self):
        while self.is_running:
            try:
                text = self.voice.listen(timeout=3)
                if not text:
                    continue
                text_lower = text.lower()
                for wake in self.wake_words:
                    if wake in text_lower:
                        print(f"[INFO] Услышал имя: {wake}")
                        self.is_active = True
                        command = self._extract_command(text, wake)
                        if command:
                            print(f"[INFO] Команда: {command}")
                            self._process_command(command)
                        else:
                            # Ждём следующую фразу
                            time.sleep(0.5)
                            second_text = self.voice.listen(timeout=5)
                            if second_text:
                                self._process_command(second_text)
                        self.is_active = False
                        break
            except Exception as e:
                print(f"[ERROR] Ошибка прослушивания: {e}")
                time.sleep(1)

    def _extract_command(self, text, wake_word):
        # Удаляем слово пробуждения и пунктуацию
        command = re.sub(rf'{wake_word}[,.\s]*', '', text, flags=re.IGNORECASE)
        return command.strip()

    def _process_command(self, command):
        if not command:
            return
        print(f"[INFO] Выполняю команду: {command}")
        result = self.agent.think_and_act(command, use_voice=True)
        if result:
            self.agent.speak(result)

    def set_wake_word(self, new_words):
        if isinstance(new_words, str):
            new_words = [new_words]
        self.wake_words = [w.lower() for w in new_words]
        print(f"[INFO] Имя(ена) активации изменено на: {', '.join(self.wake_words)}")
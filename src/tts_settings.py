import pyttsx3
import logging
from src.settings_manager import SettingsManager

logger = logging.getLogger(__name__)
settings = SettingsManager()

class TTSEngine:
    def __init__(self):
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            self.engine = pyttsx3.init()
            # Применяем настройки
            rate = settings.get("tts_rate", 150)
            volume = settings.get("tts_volume", 0.9)
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            # Выбор голоса
            voice_name = settings.get("tts_voice", "default")
            if voice_name != "default":
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if voice_name in voice.name or voice_name in voice.id:
                        self.engine.setProperty('voice', voice.id)
                        break
        except Exception as e:
            logger.error(f"TTS init error: {e}")
            self.engine = None

    def speak(self, text):
        if self.engine is None:
            self._init_engine()
            if self.engine is None:
                return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS speak error: {e}")

    def get_voices(self):
        if self.engine is None:
            self._init_engine()
        if self.engine:
            return [v.name for v in self.engine.getProperty('voices')]
        return []

    def set_voice(self, name):
        settings.set("tts_voice", name)
        self._init_engine()

    def set_rate(self, rate):
        settings.set("tts_rate", rate)
        self._init_engine()

    def set_volume(self, volume):
        settings.set("tts_volume", volume)
        self._init_engine()
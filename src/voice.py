import speech_recognition as sr
import pyttsx3
import logging

logger = logging.getLogger(__name__)

class VoiceInterface:
    def __init__(self, lang: str = "ru-RU", speed: int = 150):
        self.lang = lang
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', speed)
            self.tts_engine.setProperty('volume', 0.9)
        except Exception as e:
            logger.warning(f"TTS не доступен: {e}")
            self.tts_engine = None
    
    def listen(self, timeout: int = 5) -> str:
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("🎤 Слушаю...")
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio, language=self.lang)
                return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return "[неразборчиво]"
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            return ""
    
    def speak(self, text: str):
        if not text or not self.tts_engine:
            return
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"Ошибка озвучивания: {e}")
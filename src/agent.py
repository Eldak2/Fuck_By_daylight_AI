import logging
from datetime import datetime
from src.text_agent import TextAgent
from src.strategist import Strategist
from src.tactician import Tactician
from src.imitation_learning import ImitationLearning
from src.web_search import WebSearch
from src.context_memory import ContextMemory
from src.wake_word import WakeWordDetector
from src.voice import VoiceInterface
from src.memory import ShortTermMemory
from config.settings import Settings

from src.handlers.system_handler import SystemHandler
from src.handlers.app_handler import AppHandler
from src.handlers.media_handler import MediaHandler
from src.handlers.network_handler import NetworkHandler
from src.handlers.window_handler import WindowHandler
from src.handlers.clipboard_handler import ClipboardHandler
from src.handlers.torrent_handler import TorrentHandler
from src.handlers.registry_handler import RegistryHandler
from src.handlers.automation_handler import AutomationHandler
from src.handlers.notification_handler import NotificationHandler
from src.handlers.email_handler import EmailHandler
from src.handlers.update_handler import UpdateHandler
from src.handlers.overlay_handler import OverlayHandler

from src.combat_controller import CombatController
from src.lama_chat import LamaChatWindow

logger = logging.getLogger(__name__)

class PCAgent:
    def __init__(self, use_voice: bool = True):
        self.model_name = Settings.TEXT_MODEL
        self.max_retries = Settings.MAX_RETRIES
        self.use_voice = use_voice

        self.text_agent = TextAgent()
        self.strategist = Strategist()
        self.tactician = Tactician()
        self.imitation = ImitationLearning(self)
        self.web = WebSearch()
        self.memory = ContextMemory()
        self.stm = ShortTermMemory()
        self.voice = VoiceInterface() if use_voice else None

        if use_voice:
            self.wake_detector = WakeWordDetector(self, wake_word=["вадим", "окей гугл", "ok google"])
            self.wake_detector.start_listening()
        else:
            self.wake_detector = None

        self.system = SystemHandler(self)
        self.app = AppHandler(self)
        self.media = MediaHandler(self)
        self.network = NetworkHandler(self)
        self.window = WindowHandler(self)
        self.clipboard = ClipboardHandler(self)
        self.torrent = TorrentHandler(self)
        self.registry = RegistryHandler(self)
        self.automation = AutomationHandler(self)
        self.notification = NotificationHandler(self)
        self.email = EmailHandler(self)
        self.update = UpdateHandler(self)
        self.overlay = OverlayHandler(self)

        self.combat_controller = None
        self.lama_window = None
        self.current_mode = None  # для индикации

        self.stats = {"success": 0, "fail": 0, "actions": 0}
        self._setup_system_prompt()

        self.automation.scheduler.start()
        self.update.check_for_updates(background=True)

    def _setup_system_prompt(self):
        context = self.memory.get_context()
        system_prompt = f"""
        Ты — Fuck_By_Daylight_AI v2.0.
        Твоё имя: Вадим.
        Ты общаешься с пользователем на русском языке.

        {context}

        Ты умеешь: диалоги, зрение, игры, интернет, погоду, память, приложения, планировщик, окна, музыку, систему, температуру, процессы, буфер обмена, торренты, Steam, реестр, уведомления, почту, оверлей, сценарии, макросы, обновления, веб-интерфейс, команды Windows.

        Отвечай кратко, без эмодзи. На приветствия отвечай "я тут". Для системы давай только цифры. При опасных действиях запрашивай подтверждение.
        Девиз: "Fuck around and find out!"
        """
        self.stm.set_system_prompt(system_prompt)

    def add_notification(self, text):
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.add_message('bot', f'🔔 {text}')

    def think_and_act(self, user_goal: str, use_voice: bool = True) -> str:
        self.stm.add_message("user", user_goal)
        self.memory.add_message("user", user_goal)
        goal_lower = user_goal.lower().strip()

        # ================================================================
        # 0. ЛАМА – ТОЧНОЕ СОВПАДЕНИЕ!
        # ================================================================
        if goal_lower == "лама" or goal_lower.startswith("лама "):
            if self.lama_window is None or not self.lama_window.isVisible():
                self.lama_window = LamaChatWindow(self)
                self.lama_window.show()
                result = "Окно Ламы открыто"
            else:
                self.lama_window.raise_()
                self.lama_window.activateWindow()
                result = "Окно Ламы уже открыто"
            if use_voice and self.voice:
                self.voice.speak(result)
            return result

        # ================================================================
        # 1. МГНОВЕННЫЕ ОТВЕТЫ
        # ================================================================
        quick_replies = {
            "привет": "я тут",
            "здарова": "я тут",
            "здравствуй": "я тут",
            "доброе утро": "я тут",
            "добрый день": "я тут",
            "добрый вечер": "я тут",
            "как тебя зовут": "меня зовут Вадим",
            "твоё имя": "меня зовут Вадим",
            "кто ты": "я Вадим, твой AI-напарник",
            "ты кто": "я Вадим, твой AI-напарник",
            "что ты умеешь": "я умею управлять ПК, искать в интернете, показывать погоду, открывать приложения, играть в игры, управлять музыкой, окнами, системой и многое другое",
            "твои возможности": "я умею управлять ПК, искать в интернете, показывать погоду, открывать приложения, играть в игры, управлять музыкой, окнами, системой и многое другое",
            "что ты можешь": "я умею управлять ПК, искать в интернете, показывать погоду, открывать приложения, играть в игры, управлять музыкой, окнами, системой и многое другое",
            "как дела": "нормально, работаю",
            "что делаешь": "слушаю тебя",
            "чем занимаешься": "жду твоих команд",
            "расскажи": "о чём именно?",
            "объясни": "объясни, что именно?",
            "почему": "почему что?",
            "что такое": "что именно?",
            "помоги": "чем помочь?",
            "подскажи": "подсказать что?",
            "посоветуй": "посоветовать что?",
            "какой смысл": "смысл чего?",
            "что значит": "что именно значит?",
            "как понимать": "как понять что?",
            "что делать": "что именно делать?",
            "где находится": "где находится что?",
            "когда будет": "когда будет что?",
        }
        for phrase, reply in quick_replies.items():
            if phrase in goal_lower:
                if use_voice and self.voice:
                    self.voice.speak(reply)
                return reply

        # ================================================================
        # 2. ВРЕМЯ И ДАТА
        # ================================================================
        time_phrases = ["сколько времени", "который час", "текущее время",
                        "какая дата", "сегодня", "какой день", "сколько сейчас",
                        "время сейчас", "точное время"]
        if any(phrase in goal_lower for phrase in time_phrases):
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            date_str = now.strftime("%d.%m.%Y")
            day_week = now.strftime("%A")
            days_ru = {"Monday": "понедельник", "Tuesday": "вторник", "Wednesday": "среда",
                       "Thursday": "четверг", "Friday": "пятница", "Saturday": "суббота",
                       "Sunday": "воскресенье"}
            day_ru = days_ru.get(day_week, day_week)
            if "дата" in goal_lower or "сегодня" in goal_lower or "день" in goal_lower:
                result = f"Сегодня {date_str}, {day_ru}"
            else:
                result = f"Сейчас {time_str}"
            if use_voice and self.voice:
                self.voice.speak(result)
            return result

        # ================================================================
        # 3. ПОГОДА
        # ================================================================
        if "погода" in goal_lower or "температура" in goal_lower or "градус" in goal_lower:
            city = goal_lower.replace("погода", "").replace("температура", "").replace("градус", "").strip()
            if not city:
                city = "Moscow"
            result = self.network.get_weather(city)
            if use_voice and self.voice:
                self.voice.speak(result)
            return result

        # ================================================================
        # 4. ПОИСК В ИНТЕРНЕТЕ
        # ================================================================
        if any(word in goal_lower for word in ["найди", "поищи", "узнай", "найти", "поиск"]):
            query = user_goal
            for word in ["найди ", "поищи ", "узнай ", "найти ", "поиск "]:
                if word in user_goal:
                    query = user_goal.lower().replace(word, "").strip()
                    break
            result = self.network.search_web(query, open_browser=False)
            if use_voice and self.voice:
                self.voice.speak(result)
            return result

        # ================================================================
        # 5. ОТКРЫТИЕ ПРИЛОЖЕНИЙ
        # ================================================================
        if any(word in goal_lower for word in ["открой", "запусти", "открыть", "запустить", "игра"]):
            return self.app.handle(user_goal, use_voice)

        # ================================================================
        # 6. ОКНА
        # ================================================================
        if any(word in goal_lower for word in ["список окон", "закрой окно", "разверни окно", "сверни окно",
                                               "максимизируй окно", "минимизируй окно"]):
            return self.window.handle(user_goal, use_voice)

        # ================================================================
        # 7. МУЗЫКА И ГРОМКОСТЬ
        # ================================================================
        if any(word in goal_lower for word in ["музыка", "плей", "песня", "громкость", "звук"]):
            return self.media.handle(user_goal, use_voice)

        # ================================================================
        # 8. БУФЕР ОБМЕНА
        # ================================================================
        if any(word in goal_lower for word in ["скопируй", "копировать", "покажи буфер", "что в буфере",
                                               "скопируй картинку", "вставь картинку"]):
            return self.clipboard.handle(user_goal, use_voice)

        # ================================================================
        # 9. ТОРРЕНТЫ
        # ================================================================
        if any(word in goal_lower for word in ["добавь торрент", "торрент добавить", "список торрентов",
                                               "торренты", "удали торрент"]):
            return self.torrent.handle(user_goal, use_voice)

        # ================================================================
        # 10. РЕЕСТР
        # ================================================================
        if any(word in goal_lower for word in ["прочитай реестр", "запиши в реестр", "удали из реестра"]):
            return self.registry.handle(user_goal, use_voice)

        # ================================================================
        # 11. АВТОМАТИЗАЦИЯ (макросы, планировщик, сценарии)
        # ================================================================
        if any(word in goal_lower for word in ["записать макрос", "начать запись макроса", "остановить макрос",
                                               "стоп макрос", "выполнить макрос", "запустить макрос",
                                               "запланируй", "список задач", "очистить задачи", "показать задачи",
                                               "создай сценарий", "список сценариев", "выключи сценарий"]):
            return self.automation.handle(user_goal, use_voice)

        # ================================================================
        # 12. УВЕДОМЛЕНИЯ (НАПОМИНАНИЯ)
        # ================================================================
        if "напомни" in goal_lower:
            return self.notification.handle(user_goal, use_voice)

        # ================================================================
        # 13. ПОЧТА
        # ================================================================
        if any(word in goal_lower for word in ["проверь почту", "новые письма", "отправь письмо"]):
            return self.email.handle(user_goal, use_voice)

        # ================================================================
        # 14. ОБНОВЛЕНИЯ
        # ================================================================
        if any(word in goal_lower for word in ["проверь обновления", "установить обновление"]):
            return self.update.handle(user_goal, use_voice)

        # ================================================================
        # 15. СИСТЕМА (статистика, температура, процессы, питание, команды Windows)
        # ================================================================
        if any(word in goal_lower for word in ["диск", "память", "процессор", "свободно", "загруженность",
                                               "осталось", "место", "свободное", "занято", "объём", "гигабайт",
                                               "температура", "нагрев", "список процессов", "процессы",
                                               "закрой процесс", "убей процесс",
                                               "выключи пк", "перезагрузи пк", "спящий режим", "гибернация",
                                               "заблокируй экран", "режим не беспокоить", "выключи монитор",
                                               "открой папку", "выполни команду", "админ команда"]):
            return self.system.handle(user_goal, use_voice)

        # ================================================================
        # 16. АНАЛИЗ ЭКРАНА
        # ================================================================
        if any(word in goal_lower for word in ["что на экране", "покажи", "скриншот", "опиши экран", "что видишь"]):
            response = self.strategist.analyze(user_goal)
            if use_voice and self.voice:
                self.voice.speak(response)
            return response

        # ================================================================
        # 17. НОВОСТИ
        # ================================================================
        if "новости" in goal_lower:
            feed = goal_lower.replace("новости", "").strip()
            if feed:
                result = self.network.get_news(feed_url=feed)
            else:
                result = self.network.get_news()
            if use_voice and self.voice:
                self.voice.speak(result)
            return result

        # ================================================================
        # 18. ВЕБ-ИНТЕРФЕЙС
        # ================================================================
        if "открой веб-интерфейс" in goal_lower or "веб" in goal_lower:
            import webbrowser
            webbrowser.open("http://127.0.0.1:5000")
            result = "Веб-интерфейс открыт в браузере"
            if use_voice and self.voice:
                self.voice.speak(result)
            return result

        # ================================================================
        # 19. МАКРОСЫ (редактор)
        # ================================================================
        if "открой макросы" in goal_lower:
            if hasattr(self, 'overlay') and self.overlay:
                from src.macro_editor import MacroEditor
                editor = MacroEditor(self.overlay)
                editor.exec_()
                result = "Редактор макросов открыт"
            else:
                result = "Оверлей не активен"
            if use_voice and self.voice:
                self.voice.speak(result)
            return result

        # ================================================================
        # 20. РЕЖИМЫ ИГРЫ (1-5) – используют CombatVLA
        # ================================================================
        if "режим 1" in goal_lower or "запись" in goal_lower and "режим" not in goal_lower:
            if self.combat_controller is None:
                self.combat_controller = CombatController(self)
            if self.combat_controller.running:
                self.combat_controller.stop()
                result = "Боевой режим выключен"
                self.current_mode = None
            else:
                self.combat_controller.start()
                result = "Боевой режим включён (режим 1)"
                self.current_mode = 1
            if use_voice and self.voice:
                self.voice.speak(result)
            return result

        if "режим 2" in goal_lower or "self-play" in goal_lower:
            if self.combat_controller is None:
                self.combat_controller = CombatController(self)
            if self.combat_controller.running:
                self.combat_controller.stop()
                result = "Боевой режим выключен"
                self.current_mode = None
            else:
                self.combat_controller.start()
                result = "Боевой режим включён (режим 2)"
                self.current_mode = 2
            if use_voice and self.voice:
                self.voice.speak(result)
            return result

        if "режим 3" in goal_lower or "клон" in goal_lower:
            if self.combat_controller is None:
                self.combat_controller = CombatController(self)
            if self.combat_controller.running:
                self.combat_controller.stop()
                result = "Боевой режим выключен"
                self.current_mode = None
            else:
                self.combat_controller.start()
                result = "Боевой режим включён (режим 3)"
                self.current_mode = 3
            if use_voice and self.voice:
                self.voice.speak(result)
            return result

        if "режим 4" in goal_lower or "обычный" in goal_lower:
            if self.combat_controller is None:
                self.combat_controller = CombatController(self)
            if self.combat_controller.running:
                self.combat_controller.stop()
                result = "Боевой режим выключен"
                self.current_mode = None
            else:
                self.combat_controller.start()
                result = "Боевой режим включён (режим 4)"
                self.current_mode = 4
            if use_voice and self.voice:
                self.voice.speak(result)
            return result

        if "режим 5" in goal_lower or "свободный" in goal_lower:
            if self.combat_controller is None:
                self.combat_controller = CombatController(self)
            if self.combat_controller.running:
                self.combat_controller.stop()
                result = "Боевой режим выключен"
                self.current_mode = None
            else:
                self.combat_controller.start()
                result = "Боевой режим включён (режим 5)"
                self.current_mode = 5
            if use_voice and self.voice:
                self.voice.speak(result)
            return result

        # ================================================================
        # 21. ЗАПАСНОЙ ДИАЛОГ
        # ================================================================
        response = self.text_agent.chat(user_goal, self.memory.get_context())
        if use_voice and self.voice:
            self.voice.speak(response)
        return response

    def search_web(self, query, open_browser=False):
        return self.network.search_web(query, open_browser)

    def get_weather(self, city):
        return self.network.get_weather(city)

    def remember_fact(self, key, value):
        self.memory.add_fact(key, value)
        return f"Запомнил! {key}: {value}"

    def clear_memory(self):
        self.memory.clear()
        return "Память очищена!"

    def get_memory_context(self):
        return self.memory.get_context()

    def get_stats(self):
        return self.stats

    def speak(self, text):
        if self.voice:
            self.voice.speak(text)
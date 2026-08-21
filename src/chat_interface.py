import sys
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ChatWindow(QMainWindow):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.last_response = ""
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("💬 Fuck_By_Daylight_AI — Вадим")
        self.setGeometry(100, 100, 600, 750)
        self.setMinimumSize(500, 600)
        
        self.setStyleSheet("""
            QMainWindow { background: #0a0a1a; }
            QTextEdit { 
                background: #1a1a2e; 
                color: #ff6b81; 
                border: 2px solid #ff6b81; 
                border-radius: 10px; 
                padding: 10px;
                font-size: 14px;
            }
            QPushButton { 
                background: #ff6b81; 
                color: black; 
                font-weight: bold; 
                border-radius: 20px; 
                padding: 10px; 
                font-size: 13px;
            }
            QPushButton:hover { background: #ff4757; }
            QPushButton:disabled { background: #444; color: #888; }
            QLineEdit { 
                background: #1a1a2e; 
                color: #ff6b81; 
                border: 2px solid #ff6b81; 
                border-radius: 10px; 
                padding: 10px;
                font-size: 14px;
            }
            QLabel { 
                color: #ff6b81;
                font-size: 14px;
            }
            QGroupBox {
                border: 2px solid #ff6b81;
                border-radius: 10px;
                margin-top: 10px;
                color: #ff6b81;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("🎮 FUCK_BY_DAYLIGHT_AI — Вадим")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #ff6b81;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Статус
        self.status_label = QLabel("🟢 Онлайн | Имя: Вадим")
        self.status_label.setStyleSheet("color: #00ff00; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Чат
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background: #0a0a1a; color: #ff6b81; font-size: 14px;")
        layout.addWidget(self.chat_display)
        
        # Панель режимов
        modes_group = QGroupBox("🎮 Режимы игры")
        modes_layout = QHBoxLayout()
        
        self.mode_buttons = []
        modes_data = [
            ("1️⃣ Запись", self.start_recording),
            ("2️⃣ Self-play", self.start_self_play),
            ("3️⃣ Клон", self.start_cloning),
            ("4️⃣ Обычный", self.stop_all),
            ("5️⃣ Свободный", self.start_free)
        ]
        
        for text, func in modes_data:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            btn.setStyleSheet("font-size: 11px; padding: 8px;")
            modes_layout.addWidget(btn)
            self.mode_buttons.append(btn)
        
        modes_group.setLayout(modes_layout)
        layout.addWidget(modes_group)
        
        # Ввод
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("💬 Напиши сообщение или команду...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_btn = QPushButton("🚀")
        self.send_btn.setFixedWidth(60)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)
        
        # Кнопки быстрых действий
        quick_layout = QHBoxLayout()
        
        self.voice_btn = QPushButton("🎤 Активация")
        self.voice_btn.clicked.connect(self.voice_message)
        self.voice_btn.setToolTip("Скажи 'Вадим' для активации")
        quick_layout.addWidget(self.voice_btn)
        
        self.speak_btn = QPushButton("🔊 Озвучить")
        self.speak_btn.clicked.connect(self.speak_last)
        self.speak_btn.setToolTip("Озвучить последний ответ")
        quick_layout.addWidget(self.speak_btn)
        
        self.clear_btn = QPushButton("🧹 Очистить")
        self.clear_btn.clicked.connect(self.clear_chat)
        quick_layout.addWidget(self.clear_btn)
        
        self.stats_btn = QPushButton("📊 Статистика")
        self.stats_btn.clicked.connect(self.show_stats)
        quick_layout.addWidget(self.stats_btn)
        
        layout.addLayout(quick_layout)
        
        # Информация
        self.info_label = QLabel("💡 Команды: погода <город> | найди <запрос> | открой <приложение>")
        self.info_label.setStyleSheet("color: #8899aa; font-size: 11px;")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Приветствие
        self.add_message("🤖", "Привет! Я Вадим, твой ИИ-напарник!")
        self.add_message("💡", "Просто напиши вопрос или скажи 'Вадим' для голоса.")
    
    # === РЕЖИМЫ ИГРЫ ===
    def start_recording(self):
        result = self.agent.imitation.start_recording()
        self.add_message("🎮", result)
    
    def start_self_play(self):
        result = self.agent.imitation.start_self_learning()
        self.add_message("🎮", result)
    
    def start_cloning(self):
        result = self.agent.imitation.start_cloning()
        self.add_message("🎮", result)
    
    def stop_all(self):
        result = self.agent.imitation.stop_all()
        self.add_message("🎮", result)
    
    def start_free(self):
        result = self.agent.imitation.start_free_mode()
        self.add_message("🎮", result)
    
    # === ОСНОВНЫЕ МЕТОДЫ ===
    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        
        self.input_field.clear()
        self.add_message("👤", text)
        
        # Специальные команды
        cmd = text.lower()
        if cmd == "режим 1" or cmd == "запись":
            self.start_recording()
            return
        elif cmd == "режим 2" or cmd == "self-play":
            self.start_self_play()
            return
        elif cmd == "режим 3" or cmd == "клон":
            self.start_cloning()
            return
        elif cmd == "режим 4" or cmd == "обычный":
            self.stop_all()
            return
        elif cmd == "режим 5" or cmd == "свободный":
            self.start_free()
            return
        
        self.set_loading(True)
        thread = threading.Thread(target=self.execute_command, args=(text,))
        thread.daemon = True
        thread.start()
    
    def execute_command(self, text):
        try:
            response = self.agent.think_and_act(text)
            self.last_response = response
            self.add_message("🤖", response)
            self.update_status()
        except Exception as e:
            self.add_message("❌", f"Ошибка: {str(e)}")
        finally:
            self.set_loading(False)
    
    def voice_message(self):
        self.add_message("🎤", "Скажи 'Вадим' для активации...")
        # Активация происходит автоматически через WakeWordDetector
    
    def speak_last(self):
        """Озвучивает последний ответ"""
        if self.last_response:
            self.agent.speak(self.last_response)
            self.add_message("🔊", "Озвучиваю ответ...")
        else:
            self.add_message("🔊", "Нет ответа для озвучивания")
    
    def show_stats(self):
        stats = self.agent.get_stats()
        self.add_message("📊", f"Статистика:\n"
                               f"✅ Успешно: {stats.get('success', 0)}\n"
                               f"❌ Провалов: {stats.get('fail', 0)}\n"
                               f"⚡ Действий: {stats.get('actions', 0)}")
    
    def clear_chat(self):
        self.chat_display.clear()
        self.add_message("🧹", "Чат очищен")
    
    def update_status(self):
        status = self.agent.imitation.get_status() if hasattr(self.agent, 'imitation') else {}
        mode = status.get("mode", "idle")
        mode_names = {
            "recording": "Запись",
            "playing": "Self-play",
            "cloning": "Клон",
            "free": "Свободный",
            "idle": "Ожидание"
        }
        mode_text = mode_names.get(mode, "Неизвестно")
        self.status_label.setText(f"🟢 Режим: {mode_text} | Имя: Вадим")
    
    def add_message(self, sender: str, text: str):
        self.chat_display.append(f"{sender}: {text}")
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def set_loading(self, loading: bool):
        self.send_btn.setEnabled(not loading)
        self.voice_btn.setEnabled(not loading)
        self.speak_btn.setEnabled(not loading)
    
    def closeEvent(self, event):
        # Останавливаем все режимы при закрытии
        if hasattr(self.agent, 'imitation'):
            self.agent.imitation.stop_all()
        if hasattr(self.agent, 'wake_detector'):
            self.agent.wake_detector.stop_listening()
        event.accept()
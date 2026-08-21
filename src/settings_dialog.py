import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.settings_manager import SettingsManager
from src.lang_manager import LangManager
from src.tts_settings import TTSEngine

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setFixedSize(500, 400)
        self.setStyleSheet("background: #1a1a2e; color: #e0e0e0;")
        self.settings = SettingsManager()
        self.lang = LangManager()
        self.tts = TTSEngine()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Вкладки
        tabs = QTabWidget()
        tabs.addTab(self.create_lang_tab(), "Язык")
        tabs.addTab(self.create_tts_tab(), "Голос TTS")
        tabs.addTab(self.create_email_tab(), "Почта")
        tabs.addTab(self.create_notifications_tab(), "Уведомления")
        tabs.addTab(self.create_overlay_tab(), "Игровой оверлей")
        layout.addWidget(tabs)

        # Кнопка сохранения
        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save_all)
        layout.addWidget(btn_save)

    def create_lang_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Выберите язык интерфейса:"))
        self.lang_combo = QComboBox()
        for lang in self.lang.get_languages():
            self.lang_combo.addItem(lang)
        self.lang_combo.setCurrentText(self.lang.current_lang)
        layout.addWidget(self.lang_combo)
        layout.addStretch()
        return widget

    def create_tts_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Голос:"))
        self.voice_combo = QComboBox()
        voices = self.tts.get_voices()
        if voices:
            self.voice_combo.addItems(voices)
            current = self.settings.get("tts_voice")
            if current in voices:
                self.voice_combo.setCurrentText(current)
        else:
            self.voice_combo.addItem("default")
        layout.addWidget(self.voice_combo)

        layout.addWidget(QLabel("Скорость (слов/мин):"))
        self.rate_spin = QSpinBox()
        self.rate_spin.setRange(80, 300)
        self.rate_spin.setValue(self.settings.get("tts_rate", 150))
        layout.addWidget(self.rate_spin)

        layout.addWidget(QLabel("Громкость (0-1):"))
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0, 1)
        self.volume_spin.setSingleStep(0.1)
        self.volume_spin.setValue(self.settings.get("tts_volume", 0.9))
        layout.addWidget(self.volume_spin)
        layout.addStretch()
        return widget

    def create_email_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("SMTP сервер:"))
        self.smtp_edit = QLineEdit(self.settings.get("email_smtp_server"))
        layout.addWidget(self.smtp_edit)
        layout.addWidget(QLabel("IMAP сервер:"))
        self.imap_edit = QLineEdit(self.settings.get("email_imap_server"))
        layout.addWidget(self.imap_edit)
        layout.addWidget(QLabel("Логин:"))
        self.username_edit = QLineEdit(self.settings.get("email_username"))
        layout.addWidget(self.username_edit)
        layout.addWidget(QLabel("Пароль:"))
        self.password_edit = QLineEdit(self.settings.get("email_password"))
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)
        layout.addStretch()
        return widget

    def create_notifications_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.notif_check = QCheckBox("Включить фоновые уведомления")
        self.notif_check.setChecked(self.settings.get("notifications_enabled", True))
        layout.addWidget(self.notif_check)
        layout.addStretch()
        return widget

    def create_overlay_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.overlay_check = QCheckBox("Включить игровой оверлей")
        self.overlay_check.setChecked(self.settings.get("game_overlay_enabled", False))
        layout.addWidget(self.overlay_check)
        layout.addStretch()
        return widget

    def save_all(self):
        # Язык
        self.lang.set_language(self.lang_combo.currentText())
        # TTS
        self.settings.set("tts_voice", self.voice_combo.currentText())
        self.settings.set("tts_rate", self.rate_spin.value())
        self.settings.set("tts_volume", self.volume_spin.value())
        # Почта
        self.settings.set("email_smtp_server", self.smtp_edit.text())
        self.settings.set("email_imap_server", self.imap_edit.text())
        self.settings.set("email_username", self.username_edit.text())
        self.settings.set("email_password", self.password_edit.text())
        # Уведомления
        self.settings.set("notifications_enabled", self.notif_check.isChecked())
        # Оверлей
        self.settings.set("game_overlay_enabled", self.overlay_check.isChecked())
        # Перезапускаем TTS, чтобы применить настройки
        self.tts._init_engine()
        # Обновляем статус уведомлений
        if hasattr(self.parent(), 'agent'):
            agent = self.parent().agent
            if hasattr(agent, 'notification_manager'):
                if self.settings.get("notifications_enabled"):
                    agent.notification_manager.start()
                else:
                    agent.notification_manager.stop()
        self.accept()
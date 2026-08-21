import sys
import threading
import os
import json
import base64
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import requests
import webbrowser

API_URL = "http://127.0.0.1:5000"
CONFIG_FILE = "config.json"

class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 440, 580)
        self.setMinimumSize(360, 400)

        self.drag_position = None
        self.is_visible = True
        self.last_response = ""
        self.is_pinned = True
        self.menu_open = False
        self.full_opacity = False
        self.saved_opacity = 0.88
        self.is_maximized = False
        self.normal_geometry = None

        self.user_avatar_path = None
        self.ai_avatar_path = None
        self.default_user_avatar = "👤"
        self.default_ai_avatar = "🤖"

        self.config = self.load_config()
        opacity = self.config.get("opacity", 88)

        self.initUI()
        self.opacity_slider.setValue(opacity)
        self.change_opacity(opacity)

        self.check_api_status()
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_api_status)
        self.status_timer.start(10000)

        self.show()
        self.raise_()
        self.activateWindow()
        self.lama_window = None  # для хранения окна Ламы

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass

    def initUI(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        self.setStyleSheet("""
            #central {
                background: rgba(10, 10, 30, 0.88);
                border: 1px solid rgba(255, 107, 129, 0.2);
                border-radius: 16px;
            }
            QLabel {
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background: rgba(255, 107, 129, 0.08);
                color: #ff6b81;
                border: 1px solid rgba(255, 107, 129, 0.1);
                border-radius: 12px;
                padding: 5px 10px;
                font-size: 10px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: rgba(255, 107, 129, 0.2);
                border-color: #ff6b81;
            }
            QPushButton#menuBtn, QPushButton#opacityBtn, QPushButton#maximizeBtn, QPushButton#closeBtn, QPushButton#minimizeBtn, QPushButton#pinBtn {
                background: none;
                border: none;
                color: #8899aa;
                font-size: 14px;
                padding: 2px 5px;
            }
            QPushButton#menuBtn:hover, QPushButton#opacityBtn:hover, QPushButton#maximizeBtn:hover, QPushButton#closeBtn:hover, QPushButton#minimizeBtn:hover, QPushButton#pinBtn:hover {
                color: #ff6b81;
                background: rgba(255,107,129,0.1);
                border-radius: 4px;
            }
            QTextEdit {
                background: rgba(255,255,255,0.02);
                border: none;
                border-radius: 12px;
                color: #e0e0e0;
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
                padding: 4px;
            }
            QLineEdit {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,107,129,0.15);
                border-radius: 20px;
                color: #e0e0e0;
                font-size: 12px;
                padding: 6px 12px;
            }
            QLineEdit:focus {
                border-color: #ff6b81;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:horizontal {
                background: transparent;
                height: 4px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(255, 107, 129, 0.25);
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 107, 129, 0.25);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QSlider::groove:horizontal {
                border: none;
                height: 3px;
                background: rgba(255,255,255,0.08);
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ff6b81;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            #menuWidget {
                background: rgba(10, 10, 30, 0.95);
                border: 1px solid rgba(255,107,129,0.15);
                border-radius: 12px;
                padding: 6px;
            }
        """)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(5)

        # ШАПКА
        header_layout = QHBoxLayout()
        header_layout.setSpacing(3)
        title_label = QLabel('💬 <span style="color:#ff6b81;">Вадим</span>')
        title_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.status_indicator = QLabel('🟢')
        self.status_indicator.setStyleSheet("font-size: 9px;")
        header_layout.addWidget(self.status_indicator)

        self.opacity_btn = QPushButton('🔲')
        self.opacity_btn.setObjectName("opacityBtn")
        self.opacity_btn.setToolTip('Полная непрозрачность (вкл/выкл)')
        self.opacity_btn.clicked.connect(self.toggle_full_opacity)
        header_layout.addWidget(self.opacity_btn)

        self.maximize_btn = QPushButton('⛶')
        self.maximize_btn.setObjectName("maximizeBtn")
        self.maximize_btn.setToolTip('Развернуть/восстановить окно')
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        header_layout.addWidget(self.maximize_btn)

        self.menu_btn = QPushButton('⚙️')
        self.menu_btn.setObjectName("menuBtn")
        self.menu_btn.setToolTip('Меню функций')
        self.menu_btn.clicked.connect(self.toggle_menu)
        header_layout.addWidget(self.menu_btn)

        self.pin_btn = QPushButton('📌')
        self.pin_btn.setObjectName("pinBtn")
        self.pin_btn.setToolTip('Закрепить поверх всех окон')
        self.pin_btn.clicked.connect(self.toggle_pin)
        self.pin_btn.setStyleSheet("color: #ff6b81;")
        header_layout.addWidget(self.pin_btn)

        self.minimize_btn = QPushButton('−')
        self.minimize_btn.setObjectName("minimizeBtn")
        self.minimize_btn.clicked.connect(self.toggle_minimize)
        header_layout.addWidget(self.minimize_btn)

        self.close_btn = QPushButton('✕')
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.clicked.connect(self.hide_overlay)
        header_layout.addWidget(self.close_btn)

        layout.addLayout(header_layout)

        # МЕНЮ
        self.menu_widget = QWidget()
        self.menu_widget.setObjectName("menuWidget")
        self.menu_widget.setVisible(False)
        menu_layout = QVBoxLayout(self.menu_widget)
        menu_layout.setContentsMargins(4, 4, 4, 4)
        menu_layout.setSpacing(3)

        # Режимы игры
        modes_label = QLabel('🎮 Режимы игры')
        modes_label.setStyleSheet("color: #8899aa; font-size: 10px; font-weight: 600;")
        menu_layout.addWidget(modes_label)

        modes_grid = QGridLayout()
        modes_grid.setSpacing(3)
        modes_data = [
            ('📝 Запись', 'record', 'Записывает твои действия для обучения'),
            ('🧠 Self-play', 'self_play', 'ИИ играет сам и учится на своих ошибках'),
            ('👥 Клон', 'clone', 'Копирует твой стиль игры'),
            ('⏸️ Обычный', 'stop', 'Останавливает все режимы'),
            ('🔥 Свободный', 'free', 'ИИ играет как хочет (свободная воля)'),
            ('🦙 Лама (чат)', 'lama', 'Открывает отдельное окно для игровых советов')
        ]
        for text, mode_id, tooltip in modes_data:
            btn = QPushButton(text)
            btn.setProperty('mode', mode_id)
            btn.setToolTip(tooltip)
            if mode_id == 'lama':
                btn.clicked.connect(self.open_lama)  # прямой вызов
            else:
                btn.clicked.connect(lambda checked, m=mode_id: self.set_mode(m))
            modes_grid.addWidget(btn)
        menu_layout.addLayout(modes_grid)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: rgba(255,107,129,0.1);")
        menu_layout.addWidget(line)

        # Функции (без кнопок оверлея)
        func_label = QLabel('⚙️ Функции')
        func_label.setStyleSheet("color: #8899aa; font-size: 10px; font-weight: 600;")
        menu_layout.addWidget(func_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        scroll_area.setFrameShape(QFrame.NoFrame)

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(3)

        funcs = [
            ('📋 Окна', 'список окон'),
            ('❌ Закрыть окно', 'закрой окно '),
            ('🎵 Музыка', 'музыка плей'),
            ('🔊 Громкость +', 'громкость +'),
            ('🔇 Выкл звук', 'громкость выкл'),
            ('💾 Макрос запись', 'записать макрос'),
            ('▶️ Макрос выполнить', 'выполнить макрос'),
            ('🧲 Добавить торрент', 'добавь торрент '),
            ('📋 Список торрентов', 'список торрентов'),
            ('🎮 Запустить игру', 'запусти игру '),
            ('📂 Реестр чтение', 'прочитай реестр '),
            ('📝 Реестр запись', 'запиши в реестр '),
            ('🖼️ Скопировать картинку', 'скопируй картинку '),
            ('🖼️ Вставить картинку', 'вставь картинку '),
            ('📊 Статистика', 'статистика системы'),
            ('🌡️ Температура', 'температура'),
            ('📈 График', 'graph'),
            ('🔔 Проверить почту', 'проверь почту'),
            ('📩 Отправить письмо', 'отправь письмо '),
            ('⏰ Напомнить', 'напомни через 10 мин '),
            ('🔄 Проверить обновления', 'проверь обновления'),
            ('🌐 Веб-интерфейс', 'открой веб-интерфейс'),
            ('🔧 Макросы (ред)', 'открой макросы'),
            ('🔒 Блокировка', 'заблокируй экран'),
            ('🌙 Не беспокоить', 'режим не беспокоить'),
            ('🖥️ Выкл монитор', 'выключи монитор'),
            ('💤 Гибернация', 'гибернация'),
            ('⚙️ Настройки', 'settings')
        ]
        grid = QGridLayout()
        grid.setSpacing(3)
        row, col = 0, 0
        for text, cmd in funcs:
            btn = QPushButton(text)
            btn.setProperty('cmd', cmd)
            if cmd == 'graph':
                btn.clicked.connect(self.toggle_graph)
            elif cmd == 'settings':
                btn.clicked.connect(self.open_settings)
            else:
                btn.clicked.connect(lambda checked, c=cmd: self.send_command(c))
            if cmd.endswith(' '):
                btn.setStyleSheet("font-style: italic; font-size: 9px;")
            else:
                btn.setStyleSheet("font-size: 9px;")
            grid.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        scroll_layout.addLayout(grid)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        menu_layout.addWidget(scroll_area)

        layout.addWidget(self.menu_widget)

        # ЧАТ
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(120)
        self.chat_display.setMaximumHeight(300)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(255,255,255,0.02);
                border: none;
                border-radius: 12px;
                padding: 4px;
            }
        """)
        layout.addWidget(self.chat_display)

        self.typing_label = QLabel('⚡ Вадим печатает...')
        self.typing_label.setStyleSheet("color: #667; font-size: 10px; padding-left: 8px;")
        self.typing_label.setVisible(False)
        layout.addWidget(self.typing_label)

        # ВВОД
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('💬 Напиши или скажи "Вадим"...')
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton('🚀')
        self.send_btn.setFixedWidth(40)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

        # ПРОЗРАЧНОСТЬ
        opacity_layout = QHBoxLayout()
        opacity_layout.setSpacing(4)
        opacity_label = QLabel('🔆')
        opacity_label.setStyleSheet("color: #8899aa; font-size: 11px;")
        opacity_layout.addWidget(opacity_label)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(20)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(88)
        self.opacity_slider.setToolTip('Прозрачность окна')
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_value_label = QLabel('88%')
        self.opacity_value_label.setStyleSheet("color: #8899aa; font-size: 9px; min-width: 28px;")
        opacity_layout.addWidget(self.opacity_value_label)
        layout.addLayout(opacity_layout)

        # СТАТУС
        status_layout = QHBoxLayout()
        self.status_label = QLabel('🟢 Онлайн')
        self.status_label.setStyleSheet("color: #00ff88; font-size: 9px;")
        status_layout.addWidget(self.status_label)
        self.api_status = QLabel('✅ API')
        self.api_status.setStyleSheet("color: #00ff88; font-size: 9px;")
        status_layout.addStretch()
        status_layout.addWidget(self.api_status)
        layout.addLayout(status_layout)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("QSizeGrip { background: rgba(255,107,129,0.15); border-radius: 0 0 16px 0; width: 14px; height: 14px; }")
        self.size_grip.show()

        self.load_avatars()
        self.add_message('bot', 'Привет! Я Вадим, твой AI-напарник.')
        self.graph_window = None

    # ---- ПРЯМОЕ ОТКРЫТИЕ ЛАМЫ ----
    def open_lama(self):
        if self.lama_window is None or not self.lama_window.isVisible():
            from src.lama_chat import LamaChatWindow
            self.lama_window = LamaChatWindow(self)  # передаём self как родителя
            self.lama_window.show()
            # Добавляем уведомление в чат (краткое, без лишнего текста)
            self.add_message('🦙', 'Окно Ламы открыто')
        else:
            self.lama_window.raise_()
            self.lama_window.activateWindow()
            self.add_message('🦙', 'Окно Ламы уже открыто')

    # ---- ПРЯМОЕ УПРАВЛЕНИЕ РЕЖИМАМИ (через API) ----
    def set_mode(self, mode_id):
        try:
            resp = requests.post(f'{API_URL}/mode', json={'mode': mode_id}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if 'response' in data:
                    # Отображаем статус в статус-баре, но не в чате
                    self.status_label.setText(f"🟢 Режим: {data['response']}")
                else:
                    self.status_label.setText("🟢 Режим: неизвестно")
            else:
                self.status_label.setText("🔴 Ошибка режима")
                self.add_message('❌', f'Ошибка переключения режима: {resp.status_code}')
        except Exception as e:
            self.status_label.setText("🔴 Ошибка режима")
            self.add_message('❌', f'Ошибка соединения: {str(e)}')

    # ---- ОСТАЛЬНЫЕ МЕТОДЫ (без изменений) ----
    def toggle_maximize(self):
        if self.is_maximized:
            self.showNormal()
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.is_maximized = False
            self.maximize_btn.setText('⛶')
        else:
            self.normal_geometry = self.geometry()
            self.showMaximized()
            self.is_maximized = True
            self.maximize_btn.setText('⛶')

    def toggle_menu(self):
        self.menu_open = not self.menu_open
        self.menu_widget.setVisible(self.menu_open)
        self.menu_btn.setStyleSheet("color: #ff6b81;" if self.menu_open else "")

    def toggle_full_opacity(self):
        if self.full_opacity:
            val = self.saved_opacity * 100
            self.opacity_slider.setValue(int(val))
            self.change_opacity(int(val))
            self.full_opacity = False
            self.opacity_btn.setStyleSheet("")
            self.centralWidget().setStyleSheet("""
                #central {
                    background: rgba(10, 10, 30, 0.88);
                    border: 1px solid rgba(255, 107, 129, 0.2);
                    border-radius: 16px;
                }
            """)
        else:
            self.saved_opacity = self.windowOpacity()
            self.setWindowOpacity(1.0)
            self.opacity_value_label.setText("100%")
            self.full_opacity = True
            self.opacity_btn.setStyleSheet("color: #ff6b81;")
            self.centralWidget().setStyleSheet("""
                #central {
                    background: #0a0a1a;
                    border: 1px solid rgba(255, 107, 129, 0.2);
                    border-radius: 16px;
                }
            """)

    def send_command(self, cmd):
        if cmd.endswith(' '):
            text, ok = QInputDialog.getText(self, "Ввод", "Введите параметр:")
            if ok and text:
                full_cmd = cmd + text
                self.input_field.setText(full_cmd)
                self.send_message()
            return
        self.input_field.setText(cmd)
        self.send_message()

    def toggle_graph(self):
        if self.graph_window and self.graph_window.isVisible():
            self.graph_window.hide()
        else:
            try:
                from src.overlay_graph import GraphWindow
                self.graph_window = GraphWindow()
                self.graph_window.show()
            except Exception as e:
                self.add_message('bot', f'Ошибка графика: {str(e)}')

    def open_settings(self):
        from src.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self)
        dlg.exec_()

    def load_avatars(self):
        avatars_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'avatars')
        if not os.path.exists(avatars_dir):
            os.makedirs(avatars_dir)
        user_avatar_file = os.path.join(avatars_dir, 'user.png')
        ai_avatar_file = os.path.join(avatars_dir, 'ai.png')
        if os.path.exists(user_avatar_file):
            self.user_avatar_path = user_avatar_file
        if os.path.exists(ai_avatar_file):
            self.ai_avatar_path = ai_avatar_file

    def change_avatars(self):
        dlg = QDialog()
        dlg.setWindowTitle("Выбор аватарок")
        dlg.setStyleSheet("background: #1a1a2e; color: #e0e0e0;")
        dlg.setFixedSize(300, 200)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel("Выберите аватарки:"))
        btn_user = QPushButton("👤 Выбрать аватар пользователя")
        btn_user.clicked.connect(lambda: self.select_user_avatar(dlg))
        layout.addWidget(btn_user)
        btn_ai = QPushButton("🤖 Выбрать аватар ИИ")
        btn_ai.clicked.connect(lambda: self.select_ai_avatar(dlg))
        layout.addWidget(btn_ai)
        btn_reset = QPushButton("Сбросить аватарки")
        btn_reset.clicked.connect(self.reset_avatars)
        layout.addWidget(btn_reset)
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close)
        dlg.exec_()

    def select_user_avatar(self, parent=None):
        flags = self.windowFlags()
        self.setWindowFlags(flags & ~Qt.Tool)
        self.show()
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "Выберите аватар пользователя",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        self.setWindowFlags(flags)
        self.show()
        if file_path:
            self.user_avatar_path = file_path
            self.save_avatar(file_path, 'user')
            self.add_message('bot', 'Аватар пользователя обновлён')

    def select_ai_avatar(self, parent=None):
        flags = self.windowFlags()
        self.setWindowFlags(flags & ~Qt.Tool)
        self.show()
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "Выберите аватар ИИ",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        self.setWindowFlags(flags)
        self.show()
        if file_path:
            self.ai_avatar_path = file_path
            self.save_avatar(file_path, 'ai')
            self.add_message('bot', 'Аватар ИИ обновлён')

    def save_avatar(self, file_path, who):
        avatars_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'avatars')
        if not os.path.exists(avatars_dir):
            os.makedirs(avatars_dir)
        import shutil
        shutil.copy(file_path, os.path.join(avatars_dir, f'{who}.png'))

    def reset_avatars(self):
        self.user_avatar_path = None
        self.ai_avatar_path = None
        avatars_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'avatars')
        user_file = os.path.join(avatars_dir, 'user.png')
        ai_file = os.path.join(avatars_dir, 'ai.png')
        if os.path.exists(user_file):
            os.remove(user_file)
        if os.path.exists(ai_file):
            os.remove(ai_file)
        self.add_message('bot', 'Аватарки сброшены на стандартные')

    def add_message(self, sender, text):
        if sender == 'user':
            avatar = self.get_avatar_html('user')
            align = 'right'
            color = '#fff'
            bg = 'rgba(255,107,129,0.3)'
            name = 'Вы'
        else:
            avatar = self.get_avatar_html('ai')
            align = 'left'
            color = '#ff6b81'
            bg = 'rgba(255,255,255,0.05)'
            name = 'Вадим'

        html = f'''
        <div style="display: flex; align-items: flex-start; margin: 3px 0; justify-content: {align};">
            <div style="display: flex; flex-direction: column; align-items: {align}; max-width: 80%;">
                <div style="display: flex; align-items: center; gap: 4px; margin-bottom: 1px;">
                    {avatar}
                    <span style="font-size: 9px; color: #8899aa; font-weight: 600;">{name}</span>
                </div>
                <div style="background: {bg}; color: {color}; border-radius: 16px; padding: 5px 10px; border: 1px solid rgba(255,107,129,0.06); word-wrap: break-word; font-size: 12px;">
                    {text}
                </div>
            </div>
        </div>
        '''
        self.chat_display.append(html)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def get_avatar_html(self, who):
        if who == 'user':
            path = self.user_avatar_path
            default = self.default_user_avatar
        else:
            path = self.ai_avatar_path
            default = self.default_ai_avatar
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                buffer = QBuffer()
                buffer.open(QBuffer.WriteOnly)
                pixmap.save(buffer, 'PNG')
                img_data = base64.b64encode(buffer.data()).decode()
                buffer.close()
                return f'<img src="data:image/png;base64,{img_data}" style="border-radius: 50%; width: 24px; height: 24px;"/>'
        return f'<span style="font-size: 16px;">{default}</span>'

    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        self.input_field.clear()
        self.add_message('user', text)
        self.set_loading(True)
        threading.Thread(target=self.do_send, args=(text,), daemon=True).start()

    def do_send(self, text):
        try:
            resp = requests.post(f'{API_URL}/chat', json={'message': text}, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if 'response' in data and data['response']:
                    self.last_response = data['response']
                    self.add_message('bot', data['response'])
                else:
                    # если ответ пустой – ничего не добавляем
                    pass
            else:
                self.add_message('bot', f'API ошибка: {resp.status_code}')
        except Exception as e:
            self.add_message('bot', f'Ошибка соединения: {str(e)}')
        finally:
            self.set_loading(False)

    def speak_last(self):
        if self.last_response:
            try:
                requests.post(f'{API_URL}/speak', json={'text': self.last_response}, timeout=5)
                self.add_message('bot', 'Озвучиваю ответ...')
            except:
                self.add_message('bot', 'Не удалось озвучить (API не отвечает)')
        else:
            self.add_message('bot', 'Нет ответа для озвучивания')

    def show_stats(self):
        try:
            resp = requests.get(f'{API_URL}/stats', timeout=5)
            if resp.status_code == 200:
                stats = resp.json()
                self.add_message('bot', f"Статистика:\nУспешно: {stats.get('success',0)}\nПровалов: {stats.get('fail',0)}\nДействий: {stats.get('actions',0)}")
            else:
                self.add_message('bot', 'Не удалось получить статистику')
        except:
            self.add_message('bot', 'API не отвечает')

    def show_memory(self):
        self.add_message('bot', 'Память: запомнил твои предпочтения и диалоги.')

    def toggle_voice(self):
        self.add_message('bot', 'Скажи "Вадим" для активации голоса...')

    def toggle_minimize(self):
        if self.isMinimized():
            self.showNormal()
            self.minimize_btn.setText('−')
        else:
            self.showMinimized()
            self.minimize_btn.setText('□')

    def hide_overlay(self):
        self.hide()

    def show_overlay(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def set_loading(self, loading):
        self.typing_label.setVisible(loading)
        self.send_btn.setEnabled(not loading)

    def check_api_status(self):
        try:
            resp = requests.get(f'{API_URL}/status', timeout=2)
            if resp.status_code == 200:
                self.api_status.setText('✅ API')
                self.api_status.setStyleSheet("color: #00ff88; font-size: 9px;")
                self.status_indicator.setText('🟢')
                self.status_label.setText('🟢 Онлайн')
                return
        except:
            pass
        self.api_status.setText('⚠️ API выключен')
        self.api_status.setStyleSheet("color: #ff6b81; font-size: 9px;")
        self.status_indicator.setText('🔴')
        self.status_label.setText('🔴 Офлайн')

    def change_opacity(self, value):
        if self.full_opacity:
            return
        opacity = value / 100.0
        self.setWindowOpacity(opacity)
        self.opacity_value_label.setText(f"{value}%")
        self.config["opacity"] = value
        self.save_config()

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.pin_btn.setStyleSheet("color: #ff6b81;")
            self.pin_btn.setToolTip('Открепить (окно будет перекрываться другими)')
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.pin_btn.setStyleSheet("color: #8899aa;")
            self.pin_btn.setToolTip('Закрепить поверх всех окон')
        self.show()

    def resizeEvent(self, event):
        grip_size = 18
        self.size_grip.move(self.width() - grip_size, self.height() - grip_size)
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        event.accept()

    def keyPressEvent(self, event):
        if event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier) and event.key() == Qt.Key_G:
            if self.isVisible():
                self.hide()
            else:
                self.show_overlay()
            event.accept()
        else:
            super().keyPressEvent(event)

def run_overlay():
    app = QApplication(sys.argv)
    window = OverlayWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_overlay()
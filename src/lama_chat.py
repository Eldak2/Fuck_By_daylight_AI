import sys
import threading
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

API_URL = "http://127.0.0.1:5000"

class LamaChatWindow(QMainWindow):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(150, 150, 450, 500)
        self.setMinimumSize(350, 400)
        self.drag_position = None
        self.is_pinned = True
        self.full_opacity = False
        self.saved_opacity = 0.88
        self.is_maximized = False
        self.normal_geometry = None
        self.initUI()
        self.setWindowOpacity(0.88)
        self.show()
        self.raise_()
        self.activateWindow()

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
            QLabel { color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 12px; }
            QPushButton {
                background: rgba(255, 107, 129, 0.08);
                color: #ff6b81;
                border: 1px solid rgba(255, 107, 129, 0.1);
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 600;
            }
            QPushButton:hover { background: rgba(255, 107, 129, 0.2); border-color: #ff6b81; }
            QPushButton#closeBtn, QPushButton#minimizeBtn, QPushButton#pinBtn, QPushButton#opacityBtn, QPushButton#maximizeBtn {
                background: none; border: none; color: #8899aa; font-size: 14px; padding: 2px 5px;
            }
            QPushButton#closeBtn:hover, QPushButton#minimizeBtn:hover, QPushButton#pinBtn:hover,
            QPushButton#opacityBtn:hover, QPushButton#maximizeBtn:hover {
                color: #ff6b81; background: rgba(255,107,129,0.1); border-radius: 4px;
            }
            QTextEdit {
                background: rgba(255,255,255,0.02); border: none; border-radius: 12px;
                color: #e0e0e0; font-size: 12px; font-family: 'Segoe UI', sans-serif; padding: 4px;
            }
            QLineEdit {
                background: rgba(255,255,255,0.04); border: 1px solid rgba(255,107,129,0.15);
                border-radius: 20px; color: #e0e0e0; font-size: 12px; padding: 6px 12px;
            }
            QLineEdit:focus { border-color: #ff6b81; }
        """)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(5)
        header = QHBoxLayout()
        header.setSpacing(3)
        title = QLabel('🦙 <span style="color:#ff6b81;">Лама</span>')
        title.setStyleSheet("font-size: 13px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch()
        self.opacity_btn = QPushButton('🔲')
        self.opacity_btn.setObjectName("opacityBtn")
        self.opacity_btn.clicked.connect(self.toggle_full_opacity)
        header.addWidget(self.opacity_btn)
        self.maximize_btn = QPushButton('⛶')
        self.maximize_btn.setObjectName("maximizeBtn")
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        header.addWidget(self.maximize_btn)
        self.pin_btn = QPushButton('📌')
        self.pin_btn.setObjectName("pinBtn")
        self.pin_btn.clicked.connect(self.toggle_pin)
        self.pin_btn.setStyleSheet("color: #ff6b81;")
        header.addWidget(self.pin_btn)
        self.minimize_btn = QPushButton('−')
        self.minimize_btn.setObjectName("minimizeBtn")
        self.minimize_btn.clicked.connect(self.toggle_minimize)
        header.addWidget(self.minimize_btn)
        self.close_btn = QPushButton('✕')
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.clicked.connect(self.hide)
        header.addWidget(self.close_btn)
        layout.addLayout(header)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(120)
        self.chat_display.setMaximumHeight(300)
        layout.addWidget(self.chat_display)
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('💬 Спроси "Лама"...')
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        self.send_btn = QPushButton('🚀')
        self.send_btn.setFixedWidth(40)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)
        status_layout = QHBoxLayout()
        self.status_label = QLabel('🟢 Онлайн')
        self.status_label.setStyleSheet("color: #00ff88; font-size: 9px;")
        status_layout.addWidget(self.status_label)
        self.api_status = QLabel('✅ API')
        self.api_status.setStyleSheet("color: #00ff88; font-size: 9px;")
        status_layout.addStretch()
        status_layout.addWidget(self.api_status)
        layout.addLayout(status_layout)
        self.add_message('bot', 'Привет! Я Лама, твой игровой советник. Чем помочь?')

    def toggle_full_opacity(self):
        if self.full_opacity:
            val = self.saved_opacity * 100
            self.setWindowOpacity(val/100)
            self.full_opacity = False
            self.opacity_btn.setStyleSheet("")
        else:
            self.saved_opacity = self.windowOpacity()
            self.setWindowOpacity(1.0)
            self.full_opacity = True
            self.opacity_btn.setStyleSheet("color: #ff6b81;")

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.pin_btn.setStyleSheet("color: #ff6b81;")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.pin_btn.setStyleSheet("color: #8899aa;")
        self.show()

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

    def toggle_minimize(self):
        if self.isMinimized():
            self.showNormal()
            self.minimize_btn.setText('−')
        else:
            self.showMinimized()
            self.minimize_btn.setText('□')

    def add_message(self, sender, text):
        if sender == 'user':
            align = 'right'
            color = '#fff'
            bg = 'rgba(255,107,129,0.3)'
            name = 'Ты'
        else:
            align = 'left'
            color = '#ff6b81'
            bg = 'rgba(255,255,255,0.05)'
            name = 'Лама'
        html = f'''
        <div style="display: flex; align-items: flex-start; margin: 3px 0; justify-content: {align};">
            <div style="display: flex; flex-direction: column; align-items: {align}; max-width: 80%;">
                <div style="display: flex; align-items: center; gap: 4px; margin-bottom: 1px;">
                    <span style="font-size: 9px; color: #8899aa; font-weight: 600;">{name}</span>
                </div>
                <div style="background: {bg}; color: {color}; border-radius: 16px; padding: 5px 10px; border: 1px solid rgba(255,107,129,0.06); word-wrap: break-word; font-size: 12px;">
                    {text}
                </div>
            </div>
        </div>
        '''
        self.chat_display.append(html)
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        self.input_field.clear()
        self.add_message('user', text)
        self.send_btn.setEnabled(False)
        def do_send():
            try:
                # Увеличиваем таймаут до 60 секунд
                resp = requests.post(f'{API_URL}/chat', json={'message': text}, timeout=60)
                if resp.status_code == 200:
                    data = resp.json()
                    if 'response' in data:
                        self.add_message('bot', data['response'])
                    else:
                        self.add_message('bot', 'Ошибка: ' + data.get('error', 'неизвестно'))
                else:
                    self.add_message('bot', f'API ошибка: {resp.status_code}')
            except requests.exceptions.Timeout:
                self.add_message('bot', '⚠️ Превышено время ожидания. Попробуйте ещё раз.')
            except Exception as e:
                self.add_message('bot', f'Ошибка: {str(e)}')
            finally:
                self.send_btn.setEnabled(True)
        threading.Thread(target=do_send, daemon=True).start()

    def closeEvent(self, event):
        self.hide()
        event.accept()
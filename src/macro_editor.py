import json
import os
import pyautogui
import time
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

MACRO_FILE = "macros.json"

class MacroAction:
    def __init__(self, action_type, params):
        self.action_type = action_type  # 'click', 'type', 'press', 'wait', 'move'
        self.params = params

    def to_dict(self):
        return {"type": self.action_type, "params": self.params}

    @classmethod
    def from_dict(cls, data):
        return cls(data["type"], data["params"])

class Macro:
    def __init__(self, name):
        self.name = name
        self.actions = []

    def add_action(self, action):
        self.actions.append(action)

    def to_dict(self):
        return {"name": self.name, "actions": [a.to_dict() for a in self.actions]}

    @classmethod
    def from_dict(cls, data):
        macro = cls(data["name"])
        macro.actions = [MacroAction.from_dict(a) for a in data["actions"]]
        return macro

class MacroEditor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактор макросов")
        self.setModal(False)
        self.setMinimumSize(500, 400)
        self.macros = []
        self.current_macro = None
        self.load_macros()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        # Список макросов
        self.macro_list = QListWidget()
        self.macro_list.itemClicked.connect(self.load_macro)
        layout.addWidget(self.macro_list)

        # Кнопки управления макросами
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("➕ Создать")
        btn_new.clicked.connect(self.new_macro)
        btn_layout.addWidget(btn_new)
        btn_delete = QPushButton("🗑️ Удалить")
        btn_delete.clicked.connect(self.delete_macro)
        btn_layout.addWidget(btn_delete)
        btn_edit = QPushButton("✏️ Редактировать")
        btn_edit.clicked.connect(self.edit_macro)
        btn_layout.addWidget(btn_edit)
        btn_run = QPushButton("▶️ Выполнить")
        btn_run.clicked.connect(self.run_macro)
        btn_layout.addWidget(btn_run)
        layout.addLayout(btn_layout)

        # Список действий текущего макроса
        self.action_list = QListWidget()
        layout.addWidget(self.action_list)

        # Кнопки для действий
        action_btn_layout = QHBoxLayout()
        btn_add_click = QPushButton("➕ Клик")
        btn_add_click.clicked.connect(lambda: self.add_action('click'))
        action_btn_layout.addWidget(btn_add_click)
        btn_add_type = QPushButton("➕ Ввод текста")
        btn_add_type.clicked.connect(lambda: self.add_action('type'))
        action_btn_layout.addWidget(btn_add_type)
        btn_add_press = QPushButton("➕ Нажатие клавиши")
        btn_add_press.clicked.connect(lambda: self.add_action('press'))
        action_btn_layout.addWidget(btn_add_press)
        btn_add_wait = QPushButton("➕ Пауза")
        btn_add_wait.clicked.connect(lambda: self.add_action('wait'))
        action_btn_layout.addWidget(btn_add_wait)
        btn_add_move = QPushButton("➕ Движение мыши")
        btn_add_move.clicked.connect(lambda: self.add_action('move'))
        action_btn_layout.addWidget(btn_add_move)
        btn_delete_action = QPushButton("❌ Удалить действие")
        btn_delete_action.clicked.connect(self.delete_action)
        action_btn_layout.addWidget(btn_delete_action)
        layout.addLayout(action_btn_layout)

        # Сохранить/Закрыть
        btn_save_close = QPushButton("💾 Сохранить и закрыть")
        btn_save_close.clicked.connect(self.save_and_close)
        layout.addWidget(btn_save_close)

        self.refresh_macro_list()

    def load_macros(self):
        if os.path.exists(MACRO_FILE):
            try:
                with open(MACRO_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.macros = [Macro.from_dict(d) for d in data]
            except:
                self.macros = []

    def save_macros(self):
        try:
            with open(MACRO_FILE, 'w', encoding='utf-8') as f:
                json.dump([m.to_dict() for m in self.macros], f, ensure_ascii=False, indent=2)
        except:
            pass

    def refresh_macro_list(self):
        self.macro_list.clear()
        for m in self.macros:
            self.macro_list.addItem(m.name)

    def new_macro(self):
        name, ok = QInputDialog.getText(self, "Новый макрос", "Введите имя макроса:")
        if ok and name:
            macro = Macro(name)
            self.macros.append(macro)
            self.current_macro = macro
            self.refresh_macro_list()
            self.load_macro(self.macro_list.findItems(name, Qt.MatchExactly)[0])

    def delete_macro(self):
        idx = self.macro_list.currentRow()
        if idx >= 0:
            del self.macros[idx]
            self.current_macro = None
            self.refresh_macro_list()
            self.action_list.clear()

    def load_macro(self, item):
        name = item.text()
        for m in self.macros:
            if m.name == name:
                self.current_macro = m
                self.action_list.clear()
                for action in m.actions:
                    self.action_list.addItem(f"{action.action_type}: {action.params}")

    def edit_macro(self):
        if self.current_macro:
            # Можно переименовать
            new_name, ok = QInputDialog.getText(self, "Переименовать макрос", "Новое имя:", text=self.current_macro.name)
            if ok and new_name:
                self.current_macro.name = new_name
                self.refresh_macro_list()

    def run_macro(self):
        if self.current_macro:
            def run():
                for action in self.current_macro.actions:
                    if action.action_type == 'click':
                        pyautogui.click(action.params.get('x', 0), action.params.get('y', 0))
                    elif action.action_type == 'type':
                        pyautogui.write(action.params.get('text', ''))
                    elif action.action_type == 'press':
                        pyautogui.press(action.params.get('key', ''))
                    elif action.action_type == 'wait':
                        time.sleep(action.params.get('seconds', 1))
                    elif action.action_type == 'move':
                        pyautogui.moveTo(action.params.get('x', 0), action.params.get('y', 0), duration=0.5)
            threading.Thread(target=run, daemon=True).start()

    def add_action(self, action_type):
        if not self.current_macro:
            QMessageBox.warning(self, "Ошибка", "Выберите макрос")
            return
        params = {}
        if action_type == 'click':
            x, ok = QInputDialog.getInt(self, "Клик", "X:")
            if not ok: return
            y, ok = QInputDialog.getInt(self, "Клик", "Y:")
            if not ok: return
            params = {'x': x, 'y': y}
        elif action_type == 'type':
            text, ok = QInputDialog.getText(self, "Ввод текста", "Текст:")
            if not ok: return
            params = {'text': text}
        elif action_type == 'press':
            key, ok = QInputDialog.getText(self, "Нажатие клавиши", "Клавиша (например, enter):")
            if not ok: return
            params = {'key': key}
        elif action_type == 'wait':
            sec, ok = QInputDialog.getInt(self, "Пауза", "Секунд:")
            if not ok: return
            params = {'seconds': sec}
        elif action_type == 'move':
            x, ok = QInputDialog.getInt(self, "Движение мыши", "X:")
            if not ok: return
            y, ok = QInputDialog.getInt(self, "Движение мыши", "Y:")
            if not ok: return
            params = {'x': x, 'y': y}
        action = MacroAction(action_type, params)
        self.current_macro.add_action(action)
        self.action_list.addItem(f"{action_type}: {params}")

    def delete_action(self):
        idx = self.action_list.currentRow()
        if idx >= 0 and self.current_macro:
            del self.current_macro.actions[idx]
            self.action_list.takeItem(idx)

    def save_and_close(self):
        self.save_macros()
        self.accept()
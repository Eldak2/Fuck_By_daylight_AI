import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
import psutil
import subprocess

class GameOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(20, 20, 200, 120)
        self.setStyleSheet("background: rgba(0,0,0,0.7); border: 1px solid #ff6b81; border-radius: 8px; color: #ff6b81;")
        self.setFixedSize(200, 120)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)

        self.fps_label = QLabel("FPS: --")
        self.cpu_label = QLabel("CPU: --%")
        self.gpu_label = QLabel("GPU: --°C")
        self.ram_label = QLabel("RAM: --%")

        for label in [self.fps_label, self.cpu_label, self.gpu_label, self.ram_label]:
            label.setStyleSheet("color: #ff6b81; font-size: 10px;")
            layout.addWidget(label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def update_stats(self):
        self.fps_label.setText("FPS: 60 (эмуляция)")
        self.cpu_label.setText(f"CPU: {psutil.cpu_percent()}%")
        mem = psutil.virtual_memory()
        self.ram_label.setText(f"RAM: {mem.percent}%")
        try:
            out = subprocess.check_output(["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"])
            gpu_temp = out.decode().strip()
            self.gpu_label.setText(f"GPU: {gpu_temp}°C")
        except:
            self.gpu_label.setText("GPU: --°C")
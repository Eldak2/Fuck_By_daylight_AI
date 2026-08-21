import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QColor
import psutil

class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowTitle("График CPU/RAM")
        self.setGeometry(150, 150, 500, 300)
        self.setStyleSheet("background: #1a1a2e; color: #ff6b81;")
        self.cpu_data = []
        self.ram_data = []
        self.max_points = 60
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(1000)

    def initUI(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.chart_view = QChartView()
        layout.addWidget(self.chart_view)
        self.setup_chart()

    def setup_chart(self):
        self.chart = QChart()
        self.chart.setTitle("Загрузка CPU и RAM (%)")
        self.chart.setBackgroundBrush(QColor(26, 26, 46))
        self.chart.setTitleBrush(QColor(255, 107, 129))
        self.chart.legend().setVisible(True)
        self.chart.legend().setLabelColor(QColor(255, 107, 129))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.cpu_series = QLineSeries()
        self.cpu_series.setName("CPU")
        self.cpu_series.setColor(QColor(255, 107, 129))
        self.ram_series = QLineSeries()
        self.ram_series.setName("RAM")
        self.ram_series.setColor(QColor(0, 255, 136))

        self.axisX = QValueAxis()
        self.axisX.setRange(0, self.max_points)
        self.axisX.setTitleText("Секунды")
        self.axisX.setTitleBrush(QColor(255, 107, 129))
        self.axisX.setLabelsColor(QColor(255, 107, 129))
        self.axisY = QValueAxis()
        self.axisY.setRange(0, 100)
        self.axisY.setTitleText("%")
        self.axisY.setTitleBrush(QColor(255, 107, 129))
        self.axisY.setLabelsColor(QColor(255, 107, 129))

        self.chart.addSeries(self.cpu_series)
        self.chart.addSeries(self.ram_series)
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.chart.addAxis(self.axisY, Qt.AlignLeft)
        self.cpu_series.attachAxis(self.axisX)
        self.cpu_series.attachAxis(self.axisY)
        self.ram_series.attachAxis(self.axisX)
        self.ram_series.attachAxis(self.axisY)

        self.chart_view.setChart(self.chart)

    def update_graph(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        self.cpu_data.append(cpu)
        self.ram_data.append(ram)
        if len(self.cpu_data) > self.max_points:
            self.cpu_data.pop(0)
            self.ram_data.pop(0)

        self.cpu_series.clear()
        self.ram_series.clear()
        for i, (c, r) in enumerate(zip(self.cpu_data, self.ram_data)):
            self.cpu_series.append(i, c)
            self.ram_series.append(i, r)

        if len(self.cpu_data) > 1:
            self.axisX.setRange(0, len(self.cpu_data))
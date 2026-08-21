import psutil
import logging

logger = logging.getLogger(__name__)

class SystemMonitor:
    @staticmethod
    def get_stats():
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {
            "cpu": cpu,
            "ram_total": mem.total / (1024**3),
            "ram_used": mem.used / (1024**3),
            "ram_percent": mem.percent,
            "disk_total": disk.total / (1024**3),
            "disk_used": disk.used / (1024**3),
            "disk_percent": disk.percent
        }

    @staticmethod
    def alert_if_high(threshold_cpu=90, threshold_ram=90):
        stats = SystemMonitor.get_stats()
        alerts = []
        if stats["cpu"] > threshold_cpu:
            alerts.append(f"⚠️ Высокая нагрузка CPU: {stats['cpu']}%")
        if stats["ram_percent"] > threshold_ram:
            alerts.append(f"⚠️ Высокое использование RAM: {stats['ram_percent']}%")
        return alerts
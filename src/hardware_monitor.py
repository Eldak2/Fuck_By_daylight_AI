import subprocess
import re
import logging

logger = logging.getLogger(__name__)

class HardwareMonitor:
    @staticmethod
    def get_cpu_temperature():
        """Возвращает температуру CPU в градусах Цельсия (Windows)"""
        try:
            cmd = "Get-WmiObject -Class MSAcpi_ThermalZoneTemperature -Namespace root/wmi"
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                temps = re.findall(r'(\d+\.?\d*)', result.stdout)
                if temps:
                    kelvin = float(temps[0]) / 10.0
                    celsius = kelvin - 273.15
                    return round(celsius, 1)
            return None
        except Exception as e:
            logger.error(f"Ошибка получения температуры CPU: {e}")
            return None

    @staticmethod
    def get_gpu_temperature():
        """Возвращает температуру GPU через nvidia-smi (если установлен)"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
            return None
        except:
            return None
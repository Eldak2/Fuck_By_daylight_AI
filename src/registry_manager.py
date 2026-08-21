import winreg
import logging

logger = logging.getLogger(__name__)

class RegistryManager:
    @staticmethod
    def read_key(key_path: str, value_name: str = ""):
        try:
            # Разбираем путь: HKEY_LOCAL_MACHINE\Software\...
            parts = key_path.split("\\", 1)
            if len(parts) < 2:
                return "Некорректный путь"
            hive_name = parts[0].upper()
            subkey = parts[1]
            hive_map = {
                "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
                "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
                "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
                "HKEY_USERS": winreg.HKEY_USERS,
                "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
            }
            hive = hive_map.get(hive_name)
            if not hive:
                return "Неизвестный корень реестра"
            key = winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ)
            value, typ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return f"{value_name}: {value}"
        except Exception as e:
            return f"Ошибка чтения: {e}"

    @staticmethod
    def write_key(key_path: str, value_name: str, value_data: str, value_type: str = "REG_SZ"):
        try:
            parts = key_path.split("\\", 1)
            if len(parts) < 2:
                return "Некорректный путь"
            hive_name = parts[0].upper()
            subkey = parts[1]
            hive_map = {
                "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
                "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
                "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
                "HKEY_USERS": winreg.HKEY_USERS,
                "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
            }
            hive = hive_map.get(hive_name)
            if not hive:
                return "Неизвестный корень реестра"
            # Определяем тип
            typemap = {
                "REG_SZ": winreg.REG_SZ,
                "REG_DWORD": winreg.REG_DWORD,
                "REG_BINARY": winreg.REG_BINARY,
            }
            typ = typemap.get(value_type, winreg.REG_SZ)
            key = winreg.CreateKey(hive, subkey)
            winreg.SetValueEx(key, value_name, 0, typ, value_data)
            winreg.CloseKey(key)
            return f"Записано: {value_name} = {value_data}"
        except Exception as e:
            return f"Ошибка записи: {e}"

    @staticmethod
    def delete_key(key_path: str, value_name: str = ""):
        try:
            parts = key_path.split("\\", 1)
            if len(parts) < 2:
                return "Некорректный путь"
            hive_name = parts[0].upper()
            subkey = parts[1]
            hive_map = {
                "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
                "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
                "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
                "HKEY_USERS": winreg.HKEY_USERS,
                "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
            }
            hive = hive_map.get(hive_name)
            if not hive:
                return "Неизвестный корень реестра"
            key = winreg.OpenKey(hive, subkey, 0, winreg.KEY_ALL_ACCESS)
            if value_name:
                winreg.DeleteValue(key, value_name)
            else:
                winreg.DeleteKey(hive, subkey)
            winreg.CloseKey(key)
            return f"Удалено: {value_name if value_name else subkey}"
        except Exception as e:
            return f"Ошибка удаления: {e}"
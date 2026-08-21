import logging

logger = logging.getLogger(__name__)

BLACKLISTED_COMMANDS = [
    "rm -rf", "del /f", "format", "mkfs",
    "dd if=", "fdisk", "diskpart"
]

WHITELIST_ACTIONS = [
    "click", "type", "press", "hotkey", "scroll",
    "move", "drag", "right_click", "double_click",
    "wait", "screenshot", "shutdown", "restart", "sleep",
    "open_folder", "run_command", "admin_command"
]

def check_safety(action: dict) -> bool:
    action_type = action.get("type", "").lower()
    if action_type not in WHITELIST_ACTIONS:
        logger.warning(f"Действие {action_type} не в белом списке")
        return False
    if action_type in ["type", "run_command", "admin_command"]:
        text = action.get("text", "") if action_type in ["type", "run_command"] else action.get("command", "")
        text = text.lower()
        for bad_cmd in BLACKLISTED_COMMANDS:
            if bad_cmd in text:
                logger.warning(f"Обнаружена опасная команда: {bad_cmd}")
                return False
    return True

def is_action_allowed(action: dict) -> bool:
    return True
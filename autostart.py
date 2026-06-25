import os
import winreg
from pathlib import Path

BAT_PATH = Path(__file__).parent / "start.bat"
APP_NAME = "PCMonitorBot"

def set_autostart(enable: bool) -> bool:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
        )
        
        if enable:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, str(BAT_PATH))
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
                
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Autostart error: {e}")
        return False

def is_autostart_enabled() -> bool:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_QUERY_VALUE
        )
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return value == str(BAT_PATH)
    except FileNotFoundError:
        return False
    except Exception:
        return False

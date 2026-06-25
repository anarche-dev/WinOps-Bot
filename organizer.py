import os
import shutil
import time
import zipfile
import pythoncom
from win32com.client import Dispatch
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio
import winreg

from config import LARGE_FILES_DIR, DESKTOP_FILE_SIZE_MB

def get_shell_folder(name, guid, default_name):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
        try:
            path, _ = winreg.QueryValueEx(key, name)
        except FileNotFoundError:
            path, _ = winreg.QueryValueEx(key, guid)
        return Path(os.path.expandvars(path))
    except Exception:
        return Path.home() / default_name

DOWNLOADS_DIR = get_shell_folder("{374DE290-123F-4565-9164-39C4925E467B}", "{374DE290-123F-4565-9164-39C4925E467B}", "Downloads")
DESKTOP_DIR = get_shell_folder("Desktop", "Desktop", "Desktop")

if LARGE_FILES_DIR:
    LARGE_DIR = Path(LARGE_FILES_DIR)
else:
    LARGE_DIR = Path.home() / "Documents" / "Large_Desktop_Files"

LARGE_DIR.mkdir(parents=True, exist_ok=True)

IMAGES_DIR = DOWNLOADS_DIR / "Images"
DOCS_DIR = DOWNLOADS_DIR / "Documents"
ZIPS_DIR = DOWNLOADS_DIR / "Zips"
FOLDERS_DIR = DOWNLOADS_DIR / "FOLDER"
OTHERS_DIR = DOWNLOADS_DIR / "Others"

IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']
DOC_EXTS = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx', '.csv', '.ppt', '.pptx']
ZIP_EXTS = ['.zip', '.rar', '.7z', '.tar', '.gz']

IGNORED_FOLDERS = {"Images", "Documents", "Zips", "FOLDER", "Others"}

organizer_active = True
desktop_opt_active = True
bot_instance = None
bot_loop = None
admin_id = None
observer = None

def notify_bot(message):
    if bot_instance and admin_id and bot_loop:
        asyncio.run_coroutine_threadsafe(
            bot_instance.send_message(admin_id, message, parse_mode="HTML"), 
            bot_loop
        )

def create_shortcut(target_path: str, shortcut_path: str):
    try:
        pythoncom.CoInitialize()
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        shortcut.save()
    except Exception as e:
        print(f"Shortcut error: {e}")
    finally:
        pythoncom.CoUninitialize()

def get_path_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    elif path.is_dir():
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp) and os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        return total_size
    return 0

def process_desktop_item(item_path: Path, silent=False) -> str:
    if not item_path.exists() or item_path.suffix.lower() == '.lnk':
        return None

    ext = item_path.suffix.lower()
    if ext in ['.tmp', '.crdownload', '.part', '.ini']:
        return None

    try:
        size = get_path_size(item_path)
        if size > DESKTOP_FILE_SIZE_MB * 1024 * 1024:
            dest_path = LARGE_DIR / item_path.name
            counter = 1
            while dest_path.exists():
                dest_path = LARGE_DIR / f"{item_path.stem}_{counter}{item_path.suffix}"
                counter += 1
                
            shutil.move(str(item_path), str(dest_path))
            
            shortcut_path = str(item_path) + ".lnk"
            create_shortcut(str(dest_path), shortcut_path)
            
            msg = f"🧹 <b>Desktop Optimized</b>: \n<code>{item_path.name}</code> (>{DESKTOP_FILE_SIZE_MB}MB) was moved to <code>{LARGE_DIR.name}</code>. A shortcut was left on the desktop."
            if not silent:
                notify_bot(msg)
            return msg
    except Exception as e:
        print(f"Error processing desktop file {item_path.name}: {e}")
    return None

class DesktopHandler(FileSystemEventHandler):
    def on_created(self, event):
        global desktop_opt_active
        if not desktop_opt_active:
            return
        time.sleep(2)
        item_path = Path(event.src_path)
        if item_path.exists() and item_path.parent == DESKTOP_DIR:
            process_desktop_item(item_path, silent=False)

def optimize_existing_desktop() -> int:
    count = 0
    if not DESKTOP_DIR.exists():
        return count
    for item in DESKTOP_DIR.iterdir():
        res = process_desktop_item(item, silent=True)
        if res:
            count += 1
    return count

def set_desktop_opt_active(state: bool):
    global desktop_opt_active
    desktop_opt_active = state


def process_item(item_path: Path, silent=False) -> str:
    if not item_path.exists():
        return None
    if item_path.parent != DOWNLOADS_DIR:
        return None
        
    if item_path.name in IGNORED_FOLDERS:
        return None
        
    if item_path.is_dir():
        dest_dir = FOLDERS_DIR
        dest_dir.mkdir(exist_ok=True)
        try:
            dest_path = dest_dir / item_path.name
            counter = 1
            while dest_path.exists():
                dest_path = dest_dir / f"{item_path.name}_{counter}"
                counter += 1
                
            shutil.move(str(item_path), str(dest_path))
            msg = f"📁 <b>{item_path.name}</b> moved to <code>FOLDER</code>"
            if not silent:
                notify_bot(msg)
            return msg
        except Exception as e:
            print(f"Error moving folder {item_path.name}: {e}")
            return None

    ext = item_path.suffix.lower()
    
    if ext in ['.tmp', '.crdownload', '.part', '.ini']:
        return None

    if ext in IMAGE_EXTS:
        dest_dir = IMAGES_DIR
    elif ext in DOC_EXTS:
        dest_dir = DOCS_DIR
    elif ext in ZIP_EXTS:
        dest_dir = ZIPS_DIR
    else:
        if not ext:
            dest_dir = OTHERS_DIR
        else:
            folder_name = ext.lstrip('.').upper()
            dest_dir = DOWNLOADS_DIR / folder_name
            IGNORED_FOLDERS.add(folder_name)
            
    dest_dir.mkdir(exist_ok=True)
    
    try:
        dest_path = dest_dir / item_path.name
        counter = 1
        while dest_path.exists():
            dest_path = dest_dir / f"{item_path.stem}_{counter}{item_path.suffix}"
            counter += 1
            
        shutil.move(str(item_path), str(dest_path))
        msg = f"📂 <b>{item_path.name}</b> moved to <code>{dest_dir.name}</code>"
        
        if ext == '.zip':
            extract_dir = dest_dir / item_path.stem
            extract_dir.mkdir(exist_ok=True)
            try:
                with zipfile.ZipFile(dest_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                msg += f"\n📦 Extracted to <code>{item_path.stem}</code>"
                IGNORED_FOLDERS.add(item_path.stem)
            except Exception as e:
                msg += f"\n❌ Failed to extract: {e}"

        if not silent:
            notify_bot(msg)
        return msg
            
    except Exception as e:
        print(f"Error moving file {item_path.name}: {e}")
        return None

class DownloadsHandler(FileSystemEventHandler):
    def on_created(self, event):
        global organizer_active
        if not organizer_active:
            return
            
        time.sleep(2)
        item_path = Path(event.src_path)
        if item_path.exists() and item_path.parent == DOWNLOADS_DIR:
            process_item(item_path, silent=False)


def sort_existing_files() -> int:
    count = 0
    if not DOWNLOADS_DIR.exists():
        return count
        
    for item in DOWNLOADS_DIR.iterdir():
        res = process_item(item, silent=True)
        if res:
            count += 1
    return count

def start_organizer(bot, loop, admin):
    global observer, bot_instance, bot_loop, admin_id, organizer_active
    bot_instance = bot
    bot_loop = loop
    admin_id = admin
    
    for item in DOWNLOADS_DIR.iterdir():
        if item.is_dir():
            if item.name.isupper() and len(item.name) <= 5:
                IGNORED_FOLDERS.add(item.name)
    
    if observer is None:
        observer = Observer()
        
        if DOWNLOADS_DIR.exists():
            dl_handler = DownloadsHandler()
            observer.schedule(dl_handler, str(DOWNLOADS_DIR), recursive=False)
        else:
            print(f"Warning: Downloads folder not found at {DOWNLOADS_DIR}")
        
        if DESKTOP_DIR.exists():
            desktop_handler = DesktopHandler()
            observer.schedule(desktop_handler, str(DESKTOP_DIR), recursive=False)
        else:
            print(f"Warning: Desktop folder not found at {DESKTOP_DIR}")
        
        observer.start()

def set_organizer_active(state: bool):
    global organizer_active
    organizer_active = state

def stop_organizer():
    global observer
    if observer:
        observer.stop()
        observer.join()

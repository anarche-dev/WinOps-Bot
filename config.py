import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

LARGE_FILES_DIR = os.getenv("LARGE_FILES_DIR", "")
DESKTOP_FILE_SIZE_MB = int(os.getenv("DESKTOP_FILE_SIZE_MB", 50))

ALERT_CPU_THRESHOLD = float(os.getenv("ALERT_CPU_THRESHOLD", 90))
ALERT_RAM_THRESHOLD = float(os.getenv("ALERT_RAM_THRESHOLD", 90))
ALERT_DISK_THRESHOLD = float(os.getenv("ALERT_DISK_THRESHOLD", 90))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID is not set in .env")

# WinOps-Bot (PC Monitor & Organizer) 🤖💻

[![Demo Video](https://img.youtube.com/vi/SuOKCfy8ekA/0.jpg)](https://youtu.be/SuOKCfy8ekA)

*(Click the image to watch the video demo on YouTube)*

A fully automated, headless background utility for Windows monitoring, desktop optimization, and file organization. Built as a showcase of system integration and process automation capabilities.

## 🚀 Core Features

*   **Headless Execution & Tray Icon:** The script launches entirely in the background (headless). It only shows a tray icon next to the clock, from which it can be controlled or closed.
*   **Smart File Organizer:** Monitors the `Downloads` folder in real-time using `watchdog`. Automatically sorts images, documents, and archives into categorized folders. Auto-extracts `.zip` archives into separate folders.
*   **Desktop Optimization:** Scans the Desktop and automatically moves files larger than the configured size (default 50MB) to a dedicated folder. Leaves a Windows shortcut (`.lnk`) on your Desktop pointing to the moved file!
*   **PC Monitoring & Alerts:** Sends Telegram alerts when CPU or RAM usage exceeds critical limits (e.g., 90%). 
*   **Autostart Control:** Modify the Windows Registry to add/remove the script from automatic startup directly via a Telegram button.
*   **Remote Command Execution:** Securely execute Windows shell commands remotely via Telegram and receive the terminal output.

## 🛠️ Tech Stack

*   **Language:** Python 3
*   **Bot Framework:** `aiogram 3.x` (Asynchronous Telegram API)
*   **System Metrics:** `psutil`
*   **File System Events:** `watchdog`
*   **System Tray:** `pystray` + `Pillow`
*   **OS Integration:** Windows Registry API (`winreg`) and Windows COM interfaces (`win32com`)

## 🔒 Privacy & Security

*   All processing is done **100% locally**. 
*   The Telegram bot interface is locked to a specific `ADMIN_ID` via `.env` configuration, preventing any unauthorized remote access to the host machine.

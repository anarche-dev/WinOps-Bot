# PCMonitorBot

This is a personal script I wrote to monitor my PC via Telegram and sort my downloads automatically.

### Setup
1. Copy `.env.example` to `.env`
2. Add your bot token and telegram user ID
3. Run `start.bat`

The bot runs silently in the system tray and lets you control your PC straight from Telegram.

### What it does
- **Check PC Status**: View CPU and RAM usage directly in the chat.
- **Sort Downloads**: Automatically sorts files in the Downloads folder into Images, Documents, and Zips.
- **Optimize Desktop**: Moves large files (default >50MB) from the Desktop to a separate folder and leaves a shortcut in their place.
- **Autostart**: Add or remove the script from Windows autostart using a single button.

### Customization
If you want to change where the large desktop files go or the file size limit, you can add these to your `.env` file:
```ini
LARGE_FILES_DIR=C:\Your\Custom\Folder
DESKTOP_FILE_SIZE_MB=100
```

### Dependencies
I used `pywin32` for the Windows shortcuts, `watchdog` to monitor the folders, and `pystray` for the system tray icon. Check `requirements.txt` for the full list.

import asyncio
import logging
import threading
import sys
import os
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, ADMIN_ID
from handlers import router
from background import monitoring_task
from organizer import start_organizer, stop_organizer

import pystray
from PIL import Image, ImageDraw

logging.basicConfig(level=logging.INFO)

bot_loop = None

def create_image():
    image = Image.new('RGB', (64, 64), color = (52, 152, 219))
    d = ImageDraw.Draw(image)
    d.rectangle([16, 16, 48, 48], fill=(41, 128, 185))
    return image

def on_quit(icon, item):
    icon.stop()
    stop_organizer()
    if bot_loop:
        bot_loop.call_soon_threadsafe(bot_loop.stop)
    os._exit(0)

def run_tray():
    icon = pystray.Icon(
        "PCMonitorBot", 
        create_image(), 
        "PC Monitor Bot", 
        menu=pystray.Menu(pystray.MenuItem("Quit", on_quit))
    )
    def setup(icon):
        icon.visible = True
        icon.notify('Bot is running in the background.', 'PC Monitor Bot')

    icon.run(setup)

def run_bot():
    global bot_loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot_loop = loop
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    loop.create_task(monitoring_task(bot))
    start_organizer(bot, loop, ADMIN_ID)
    
    try:
        loop.run_until_complete(dp.start_polling(bot))
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    run_tray()

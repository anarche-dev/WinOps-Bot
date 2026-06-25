import asyncio
import logging
from aiogram import Bot
from monitor import get_cpu_usage, get_ram_usage, get_disk_usage
from config import ADMIN_ID, ALERT_CPU_THRESHOLD, ALERT_RAM_THRESHOLD, ALERT_DISK_THRESHOLD

async def monitoring_task(bot: Bot):
    while True:
        try:
            cpu = get_cpu_usage()
            ram = get_ram_usage()
            disk = get_disk_usage()
            
            alerts = []
            
            if cpu > ALERT_CPU_THRESHOLD:
                alerts.append(f"⚠️ <b>High CPU Usage!</b> ({cpu}%)")
            
            if ram['percent'] > ALERT_RAM_THRESHOLD:
                alerts.append(f"⚠️ <b>High RAM Usage!</b> ({ram['percent']}%)")
                
            if disk.get('percent', 0) > ALERT_DISK_THRESHOLD:
                alerts.append(f"⚠️ <b>Low Disk Space!</b> ({disk['percent']}% used)")
                
            if alerts:
                alert_msg = "🚨 <b>SYSTEM ALERT</b> 🚨\n\n" + "\n".join(alerts)
                await bot.send_message(ADMIN_ID, alert_msg, parse_mode="HTML")
                
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Error in monitoring task: {e}")
            await asyncio.sleep(60)

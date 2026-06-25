import psutil

def get_cpu_usage() -> float:
    return psutil.cpu_percent(interval=1)

def get_ram_usage() -> dict:
    mem = psutil.virtual_memory()
    return {
        "percent": mem.percent,
        "used_gb": round(mem.used / (1024 ** 3), 2),
        "total_gb": round(mem.total / (1024 ** 3), 2)
    }

def get_disk_usage(path="C:\\") -> dict:
    try:
        disk = psutil.disk_usage(path)
        return {
            "percent": disk.percent,
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "total_gb": round(disk.total / (1024 ** 3), 2)
        }
    except Exception as e:
        return {"percent": 0, "free_gb": 0, "total_gb": 0, "error": str(e)}

def get_system_status() -> str:
    cpu = get_cpu_usage()
    ram = get_ram_usage()
    disk = get_disk_usage()
    
    status = (
        f"🖥 <b>System Status</b>\n\n"
        f"⚙️ <b>CPU:</b> {cpu}%\n"
        f"🧠 <b>RAM:</b> {ram['used_gb']}GB / {ram['total_gb']}GB ({ram['percent']}%)\n"
        f"💾 <b>Disk (C:):</b> {disk['free_gb']}GB free of {disk['total_gb']}GB ({disk['percent']}% used)\n"
    )
    return status

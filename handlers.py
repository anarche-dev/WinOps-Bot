from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from config import ADMIN_ID, DESKTOP_FILE_SIZE_MB
from monitor import get_system_status
import subprocess
import os
import organizer
import autostart

router = Router()

def is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🖥 Status"), KeyboardButton(text="📁 Organizer Toggle")],
        [KeyboardButton(text="🧹 Sort Existing"), KeyboardButton(text="🚀 Autostart Toggle")],
        [KeyboardButton(text="🧹 Optimize Desktop"), KeyboardButton(text="🖥 Desktop Opt Toggle")],
        [KeyboardButton(text="💎 Creator's Channel"), KeyboardButton(text="🔄 Stop Bot")]
    ],
    resize_keyboard=True
)

inline_creator_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Subscribe", url="https://t.me/godanarche")]
    ]
)

@router.message(CommandStart())
async def cmd_start(message: Message):
    if not is_admin(message):
        await message.answer("Access denied.")
        return
    await message.answer("Welcome to PC Monitor Bot! I am monitoring your system.", reply_markup=menu_keyboard)

@router.message(F.text == "💎 Creator's Channel")
async def cmd_creator(message: Message):
    if not is_admin(message):
        return
    await message.answer("Subscribe to the creator's channel 👇", reply_markup=inline_creator_kb)

@router.message(Command("status"))
@router.message(F.text == "🖥 Status")
async def cmd_status(message: Message):
    if not is_admin(message):
        return
    status_text = get_system_status()
    await message.answer(status_text, parse_mode="HTML")

@router.message(F.text == "📁 Organizer Toggle")
async def cmd_organizer_toggle(message: Message):
    if not is_admin(message):
        return
    new_state = not organizer.organizer_active
    organizer.set_organizer_active(new_state)
    state_str = "ON 🟢" if new_state else "OFF 🔴"
    await message.answer(f"File Organizer is now {state_str}")

@router.message(F.text == "🧹 Sort Existing")
async def cmd_sort_existing(message: Message):
    if not is_admin(message):
        return
    await message.answer("Starting bulk sort of the Downloads folder... ⏳")
    count = organizer.sort_existing_files()
    await message.answer(f"✅ Sorting complete! Successfully moved {count} files.")

@router.message(F.text == "🧹 Optimize Desktop")
async def cmd_optimize_desktop(message: Message):
    if not is_admin(message):
        return
    await message.answer(f"Scanning Desktop for files and folders larger than {DESKTOP_FILE_SIZE_MB}MB... ⏳")
    count = organizer.optimize_existing_desktop()
    await message.answer(f"✅ Desktop optimization complete! Moved and created shortcuts for {count} large items.")

@router.message(F.text == "🖥 Desktop Opt Toggle")
async def cmd_desktop_toggle(message: Message):
    if not is_admin(message):
        return
    current_state = organizer.desktop_opt_active
    new_state = not current_state
    organizer.set_desktop_opt_active(new_state)
    state_str = "ON 🟢" if new_state else "OFF 🔴"
    await message.answer(f"Desktop Optimization (Live Monitoring) is now {state_str}")

@router.message(Command("cmd"))
async def cmd_run(message: Message):
    if not is_admin(message):
        return
    command = message.text.replace("/cmd ", "").strip()
    if not command or command == "/cmd":
        await message.answer("Please provide a command. Example: /cmd ping 8.8.8.8")
        return

    await message.answer(f"Running command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout if result.stdout else result.stderr
        if not output:
            output = "Command executed with no output."
        if len(output) > 4000:
            output = output[:4000] + "\n...[truncated]"
        await message.answer(f"<pre>{output}</pre>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"Error executing command: {e}")

@router.message(F.text == "🚀 Autostart Toggle")
async def cmd_autostart_toggle(message: Message):
    if not is_admin(message):
        return
    current_state = autostart.is_autostart_enabled()
    new_state = not current_state
    success = autostart.set_autostart(new_state)
    
    if success:
        state_str = "ON 🟢" if new_state else "OFF 🔴"
        await message.answer(f"Windows Autostart is now {state_str}")
    else:
        await message.answer("❌ Failed to change Autostart settings.")

@router.message(F.text == "🔄 Stop Bot")
async def cmd_stop_bot(message: Message):
    if not is_admin(message):
        return
    await message.answer("Stopping bot...")
    os._exit(0)

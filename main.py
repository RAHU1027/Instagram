import logging
import os
import threading
import asyncio
from flask import Flask
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import BotCommand
import requests

# CONFIG
API_TOKEN = '8878551213:AAEuXkfq8ZLkBZYZ7umIhrePCWKyinJObDw'
SECRET_KEY = "rk_test_51Toge60PPaNM3lnKN6oFr6JU6P4lrTtzwComE7wc6e1Nmy4BdUK2qYEKGxmNUQGbxlRkiw0ZujH1Dcu8hcvi0JZp00qtqZ7rfl"
ANIMATION_URL = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZndwZ3ZqZndwZ3ZqZndwZ3ZqZndwZ3ZqZndwZ3ZqZndwJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKVUn7iM8FMEU24/giphy.gif"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

# FORMATTING DESIGN
def get_format(cc, status, gate, bin_info, user_name):
    icon = "✅" if status == "Approved" else "❌"
    response_txt = "Card added" if status == "Approved" else "Declined"
    
    return (
        f"💳 𝗖𝗖 : <code>{cc}</code>\n"
        f"Status: {status} {icon}\n"
        f"Response: {response_txt}\n"
        f"Gateway: {gate}\n"
        f"Bank: {bin_info.get('bank', 'N/A')}\n"
        f"Type: {bin_info.get('type', 'N/A')}\n"
        f"Country: {bin_info.get('country', 'N/A')}\n"
        f"Checked by: @{user_name}\n"
        f"Credits left: Unlimited"
    )

# CHECKER LOGIC
def check_cc(cc, mm, yy, cvc):
    url = "https://api.stripe.com/v1/tokens"
    headers = {"Authorization": f"Bearer {SECRET_KEY}"}
    data = {"card[number]": cc, "card[exp_month]": mm, "card[exp_year]": yy, "card[cvc]": cvc}
    try:
        res = requests.post(url, headers=headers, data=data).json()
        if "error" in res: return "Declined", {"bank": "N/A", "type": "N/A", "country": "N/A"}
        return "Approved", {"bank": "Green Dot Bank", "type": "Visa - Debit", "country": "United States"}
    except: return "Declined", {}

# COMMANDS
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    loading = await bot.send_animation(message.chat.id, animation=ANIMATION_URL)
    await bot.delete_message(message.chat.id, message.message_id)
    await asyncio.sleep(2.5)
    await bot.delete_message(message.chat.id, loading.message_id)
    await message.answer("✅ Kushal Bot Ready! Commands menu dekhein.")

@dp.message_handler(commands=['chk'])
async def chk(message: types.Message):
    await message.reply("CC bhejein: `cc|mm|yy|cvc`")

@dp.message_handler(commands=['st'])
async def st(message: types.Message):
    await message.reply("Status: ONLINE ✅\nUptime: Active on Render")

# FILE PROCESSING
@dp.message_handler(content_types=['document'])
async def handle_docs(message: types.Message):
    file_info = await bot.get_file(message.document.file_id)
    file = await bot.download_file(file_info.file_path)
    lines = file.read().decode('utf-8').splitlines()
    
    for line in lines:
        try:
            parts = line.replace('|', ':').split(':')
            status, bin_info = check_cc(parts[0], parts[1], parts[2], parts[3])
            msg = get_format(parts[0], status, "Stripe", bin_info, message.from_user.username or "User")
            await message.reply(msg, parse_mode="HTML")
        except: continue

# WEB SERVER
@app.route('/')
def home(): return "Bot is running!"

if __name__ == '__main__':
    # Set Commands
    async def set_cmds():
        await bot.set_my_commands([
            BotCommand("start", "Start Bot"),
            BotCommand("gen", "Generate CC"),
            BotCommand("chk", "Check CC"),
            BotCommand("st", "Status"),
        ])
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_cmds())
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))).start()
    executor.start_polling(dp, skip_updates=True)

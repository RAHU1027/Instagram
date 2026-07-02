import logging
import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types, executor
import requests

# Tumhari Key
SECRET_KEY = "rk_test_51Toge60PPaNM3lnKN6oFr6JU6P4lrTtzwComE7wc6e1Nmy4BdUK2qYEKGxmNUQGbxlRkiw0ZujH1Dcu8hcvi0JZp00qtqZ7rfl"
API_TOKEN = '8878551213:AAEuXkfq8ZLkBZYZ7umIhrePCWKyinJObDw'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Flask Server
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"

# Checker Logic
def check_cc_stripe(cc, mm, yy, cvc):
    url = "https://api.stripe.com/v1/tokens"
    headers = {"Authorization": f"Bearer {SECRET_KEY}"}
    data = {"card[number]": cc, "card[exp_month]": mm, "card[exp_year]": yy, "card[cvc]": cvc}
    try:
        response = requests.post(url, headers=headers, data=data).json()
        if "error" in response: return False, response["error"]["message"]
        return True, "Approved"
    except: return False, "Error"

# File Processing
@dp.message_handler(content_types=['document'])
async def handle_docs(message: types.Message):
    document = message.document
    file_info = await bot.get_file(document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    
    lines = downloaded_file.read().decode('utf-8').splitlines()
    total = len(lines)
    approved = 0
    declined = 0
    
    await message.reply(f"📂 File mili! {total} cards check ho rahe hain...")
    
    for line in lines:
        try:
            parts = line.replace('|', ':').split(':')
            is_valid, msg = check_cc_stripe(parts[0], parts[1], parts[2], parts[3])
            if is_valid: approved += 1
            else: declined += 1
        except: continue
    
    # Result Summary
    result_text = (f"✅ Scan Complete!\n\n"
                   f"Total: {total}\n"
                   f"Approved: {approved}\n"
                   f"Declined: {declined}\n\n"
                   f"👤 User: {message.from_user.first_name}")
    
    await message.reply(result_text)
    # Group mein update (Agar tumhari group ID pata hai toh wahan bhi bhej sakte ho)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))).start()
    executor.start_polling(dp, skip_updates=True)

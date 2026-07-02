import logging
import os
import threading
import telebot
import requests
import time
import random
from flask import Flask

# CONFIG
API_TOKEN = '8744594607:AAGXRJnxQ_ylxbQO40sAQYigA5n1refYgY4'
SECRET_KEY = "sk_test_51Toge60PPaNM3lnKldVYOSTT8QFsujYTHJ02OfDWqo82B1okdG9vYItCp6bQvLcFGqCkYcQyOHgSMFLQFRQab2lz00H80IHrEc"
ANIMATION_URL = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZndwZ3ZqZndwZ3ZqZndwZ3ZqZndwZ3ZqZndwZ3ZqZndwJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l41lTjJp9tYyG2cKc/giphy.gif"

logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# BIN LOOKUP
def get_bin_info(cc):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(f"https://lookup.binlist.net/{cc[:6]}", headers=headers, timeout=5).json()
        return {
            "bank": res.get("bank", {}).get("name", "N/A"),
            "type": res.get("type", "N/A"),
            "country": res.get("country", {}).get("name", "N/A")
        }
    except: return {"bank": "N/A", "type": "N/A", "country": "N/A"}

# FORMATTING - Updated with your requested design and User Name
def get_format(cc, mm, yy, cvc, status, gate, bin_info, user_name, user_id, error_msg):
    icon = "✅" if status == "Approved" else "❌"
    status_text = "Approved" if status == "Approved" else "Declined/Maintenance 🛠"
    return (
        f"💳 CC: <code>{cc}|{mm}|{yy}|{cvc}</code>\n"
        f"📡 Status: {status_text} {icon}\n"
        f"📝 Response: {error_msg}\n"
        f"━━━━━━━━━━━━━━\n"
        f"🏦 Bank: {bin_info.get('bank', 'N/A')}\n"
        f"🌍 Country: {bin_info.get('country', 'N/A')}\n"
        f"🛠 Gateway: {gate}\n"
        f"━━━━━━━━━━━━━━\n"
        f"👤 Checked by: {user_name}\n"
        f"🆔 ID: {user_id}\n"
        f"━━━━━━━━━━━━━━"
    )

# CHECKER LOGIC
def check_cc(cc, mm, yy, cvc):
    url = "https://api.stripe.com/v1/tokens"
    headers = {"Authorization": f"Bearer {SECRET_KEY}"}
    data = {"card[number]": cc, "card[exp_month]": mm, "card[exp_year]": yy, "card[cvc]": cvc}
    try:
        res = requests.post(url, headers=headers, data=data, timeout=10).json()
        bin_info = get_bin_info(cc)
        if "error" in res: return "Declined", bin_info, res['error'].get('message', 'Declined')
        return "Approved", bin_info, "Card Approved"
    except: return "Declined", get_bin_info(cc), "Connection Error"

# COMMANDS
@bot.message_handler(commands=['start'])
def start(message):
    loading = bot.send_animation(message.chat.id, animation=ANIMATION_URL)
    time.sleep(2.5)
    bot.delete_message(message.chat.id, loading.message_id)
    bot.send_message(message.chat.id, "✨ *Welcome to KUSHAL PREMIUM BOT* ✨\n\nCommands:\n/chk cc|mm|yy|cvc - Check Card\n/gen bin - Generate\n/st - Check Status", parse_mode="Markdown")

@bot.message_handler(commands=['chk', 'st'])
def chk(message):
    try:
        data = message.text.split(' ', 1)[1]
        parts = data.replace('|', ':').replace('/', ':').split(':')
        status, bin_info, err = check_cc(parts[0], parts[1], parts[2], parts[3])
        msg = get_format(parts[0], parts[1], parts[2], parts[3], status, "Stripe", bin_info, message.from_user.first_name, message.from_user.id, err)
        bot.reply_to(message, msg, parse_mode="HTML")
    except: bot.reply_to(message, "⚠️ Format error! Use: `.chk cc|mm|yy|cvc`")

@bot.message_handler(commands=['gen'])
def gen(message):
    try:
        bin_code = message.text.split(' ')[1]
        cc = bin_code + ''.join([str(random.randint(0, 9)) for _ in range(16 - len(bin_code))])
        bot.reply_to(message, f"💳 Generated: <code>{cc}|12|2027|000</code>", parse_mode="HTML")
    except: bot.reply_to(message, "⚠️ Use: `.gen 465828`")

# WEB SERVER
@app.route('/')
def home(): return "KUSHAL BOT IS ACTIVE"

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    bot.infinity_polling()

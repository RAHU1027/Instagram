import logging
import os
import threading
from flask import Flask
import telebot 
import requests
import time

# CONFIG
API_TOKEN = '8744594607:AAGXRJnxQ_ylxbQO40sAQYigA5n1refYgY4'
SECRET_KEY = "mk_1TogeC0PPaNM3lnKl6Bk78Ur"
ANIMATION_URL = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZndwZ3ZqZndwZ3ZqZndwZ3ZqZndwZ3ZqZndwZ3ZqZndwJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l41lTjJp9tYyG2cKc/giphy.gif"

logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# BIN LOOKUP - FIX FOR N/A
def get_bin_info(cc):
    try:
        res = requests.get(f"https://lookup.binlist.net/{cc[:6]}").json()
        return {
            "bank": res.get("bank", {}).get("name", "N/A"),
            "type": res.get("type", "N/A"),
            "country": res.get("country", {}).get("name", "N/A")
        }
    except: return {"bank": "N/A", "type": "N/A", "country": "N/A"}

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
        bin_info = get_bin_info(cc)
        if "error" in res: return "Declined", bin_info
        return "Approved", bin_info
    except: return "Declined", get_bin_info(cc)

# COMMANDS
@bot.message_handler(commands=['start'])
def start(message):
    loading = bot.send_animation(message.chat.id, animation=ANIMATION_URL)
    bot.delete_message(message.chat.id, message.message_id)
    time.sleep(2.5)
    bot.delete_message(message.chat.id, loading.message_id)
    bot.send_message(message.chat.id, "✅ Kushal Bot Ready! Commands: /chk cc|mm|yy|cvc aur /st")

@bot.message_handler(commands=['chk'])
def chk(message):
    try:
        # Command se data nikalna
        input_data = message.text.split(' ', 1)[1]
        parts = input_data.replace('|', ':').split(':')
        status, bin_info = check_cc(parts[0], parts[1], parts[2], parts[3])
        msg = get_format(parts[0], status, "Stripe", bin_info, message.from_user.username or "User")
        bot.reply_to(message, msg, parse_mode="HTML")
    except:
        bot.reply_to(message, "Format galat hai! Use: `/chk cc|mm|yy|cvc`", parse_mode="Markdown")

@bot.message_handler(commands=['st'])
def st(message):
    bot.reply_to(message, "Status: ONLINE ✅\nUptime: Active on Render")

# FILE PROCESSING
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    lines = downloaded_file.decode('utf-8').splitlines()
    
    for line in lines:
        try:
            parts = line.replace('|', ':').replace(';', ':').split(':')
            status, bin_info = check_cc(parts[0], parts[1], parts[2], parts[3])
            msg = get_format(parts[0], status, "Stripe", bin_info, message.from_user.username or "User")
            bot.reply_to(message, msg, parse_mode="HTML")
        except: continue

# WEB SERVER
@app.route('/')
def home(): return "Bot is running!"

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    bot.infinity_polling()

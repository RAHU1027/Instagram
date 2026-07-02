import os
import requests
import random
import asyncio
import time
from flask import Flask
from threading import Thread
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = '8744594607:AAGXRJnxQ_ylxbQO40sAQYigA5n1refYgY4'
STRIPE_KEY = "sk_test_51Toge60PPaNM3lnKldVYOSTT8QFsujYTHJ02OfDWqo82B1okdG9vYItCp6bQvLcFGqCkYcQyOHgSMFLQFRQab2lz00H80IHrEc"
OWNER_NAME = "🦋💸 ⃪♔‌⃟𝐊𝐔𝐒𝐇𝐀𝐋 ⚠️"

# --- WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "KUSHAL BOT IS LIVE!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# --- HELPERS ---
def get_bin_info(cc_or_bin):
    try:
        res = requests.get(f"https://lookup.binlist.net/{cc_or_bin[:6]}", timeout=5).json()
        bank = res.get('bank', {}).get('name', 'N/A')
        brand = res.get('scheme', 'N/A')
        type_cc = res.get('type', 'N/A')
        country = res.get('country', {}).get('name', 'N/A')
        return bank, f"{brand.upper()} - {type_cc.upper()} - Standard", country
    except: return "N/A", "N/A", "N/A"

def luhn_checksum(card_number):
    digits = [int(d) for d in card_number]
    for i in range(len(digits) - 2, -1, -2):
        n = digits[i] * 2
        digits[i] = n if n < 10 else n - 9
    return (10 - (sum(digits) % 10)) % 10

# --- COMMANDS ---
async def start(update, context):
    r_emoji = random.choice(["🔥", "✨", "🚀", "💎", "⚡"])
    msg = await update.message.reply_text(f"{r_emoji} 𝗜𝗡𝗜𝗧𝗜𝗔𝗟𝗜𝗭𝗜𝗡𝗚 𝗦𝗬𝗦𝗧𝗘𝗠...")
    await asyncio.sleep(0.5)
    await msg.edit_text(f"{r_emoji} 𝗟𝗢𝗔𝗗𝗜𝗡𝗚: [■■■■■■■■■■] 100%")
    await asyncio.sleep(0.4)
    await msg.delete()
    caption = f"✨ <b>Welcome to KUSHAL PREMIUM BOT</b> ✨\n👤 <b>Owner:</b> {OWNER_NAME}\n\nCommands: /chk [cc|mm|yy|cvc], /gen [bin]"
    await update.message.reply_text(caption, parse_mode=constants.ParseMode.HTML)

# --- CHECKER (/chk) ---
async def chk(update, context):
    try:
        data = context.args[0]
        parts = data.replace('|', ':').replace('/', ':').split(':')
        cc, mm, yy, cvc = parts[0], parts[1], parts[2], parts[3]
        
        url = "https://api.stripe.com/v1/tokens"
        res = requests.post(url, headers={"Authorization": f"Bearer {STRIPE_KEY}"}, 
                            data={"card[number]": cc, "card[exp_month]": mm, "card[exp_year]": yy, "card[cvc]": cvc}).json()
        
        status = "Approved ✅" if "card" in res else "Declined ❌"
        err = res.get('error', {}).get('message', 'Card added')
        bank, full_type, country = get_bin_info(cc)
        user_name = update.effective_user.first_name
        
        # Design requested
        msg = (f"CC: <code>{cc}|{mm}|{yy}|{cvc}</code>\n"
               f"Status: {status}\n"
               f"Response: {err}\n"
               f"Gateway: Stripe\n"
               f"Bank: {bank}\n"
               f"Type: {full_type}\n"
               f"Country: {country}\n"
               f"Checked by: {user_name}\n"
               f"Credits left: 0")
        await update.message.reply_text(msg, parse_mode=constants.ParseMode.HTML)
    except: await update.message.reply_text("⚠️ Use: /chk cc|mm|yy|cvc")

# --- GENERATOR (/gen) ---
async def gen(update, context):
    if not context.args:
        await update.message.reply_text("❌ Use: /gen [bin]")
        return
    bin_input = context.args[0]
    start_t = time.time()
    bank, full_type, country = get_bin_info(bin_input)
    cc_list = [f"<code>{bin_input[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)]) + str(luhn_checksum(bin_input[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)])))}|{str(random.randint(1, 12)).zfill(2)}|{random.randint(2026, 2036)}|{random.randint(100, 999)}</code>" for _ in range(10)]
    
    # Design requested
    final_text = (f"𝙆𝙐𝙎𝙃𝘼𝙇 𝘽𝙊𝙏 🍁:\n[+] 𝙂𝙀𝙉𝙀𝙍𝘼𝙏𝙀𝘿 𝘾𝘼𝙍𝘿𝙎\n\n" + "\n".join(cc_list) + 
                  f"\n\n──────────────\n💳 𝘽𝙄𝙉: {bin_input}\n🏦 𝘽𝘼𝙉𝙆: {bank}\n📡 𝙏𝙔𝙋𝙀: {full_type}\n🌍 𝘾𝙊𝙐𝙉𝙏𝙍𝙔: {country}\n"
                  f"──────────────\n⏰ 𝙏𝙄𝙈𝙀: {round(time.time() - start_t, 2)}s\n👤 𝙊𝙒𝙉𝙀𝙍: {OWNER_NAME}")
    await update.message.reply_text(final_text, parse_mode=constants.ParseMode.HTML)

# --- MAIN ---
if __name__ == '__main__':
    Thread(target=run_web, daemon=True).start()
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("chk", chk))
    app_bot.add_handler(CommandHandler("st", chk))
    app_bot.add_handler(CommandHandler("gen", gen))
    app_bot.run_polling()

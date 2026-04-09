import telebot
from telebot import types
import threading
import time
import random
import os
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from datetime import datetime

# --- কনফিগারেশন ---
API_TOKEN = '8615640384:AAHuqDZuv7zzxtvgUMwlAg6i1hrAHizcqC4'
bot = telebot.TeleBot(API_TOKEN)

# ভেরিয়েবল (অরিজিনাল লজিক অনুযায়ী)
user_data = {}
ua = UserAgent()

# --- মূল অটোমেশন ইঞ্জিন (যা প্রতি ১০ সেকেন্ড পর রিসেট হবে - একদম অপরিবর্তিত) ---
def run_automation(chat_id, url, threads_count):
    user_data[chat_id]['running'] = True
    
    def worker():
        while user_data.get(chat_id, {}).get('running', False):
            driver = None
            try:
                # ১. নতুন ব্রাউজার প্রোফাইল ও ইউজার এজেন্ট তৈরি
                options = uc.ChromeOptions()
                current_ua = ua.random
                
                options.add_argument(f'--user-agent={current_ua}')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--incognito')
                
                # --- ক্লাউড সার্ভার ইস্যু ফিক্স (Binary Location Error সমাধানের জন্য) ---
                options.add_argument('--headless') # সার্ভারে ডিসপ্লে নেই তাই হেডলেস
                options.add_argument('--no-sandbox') # Root ইউজার ইস্যু ফিক্স
                options.add_argument('--disable-dev-shm-usage') # মেমোরি ক্র্যাশ ফিক্স
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1280,720')
                
                # ২. ব্রাউজার চালু করা (Undetected Mode)
                now = datetime.now().strftime("%H:%M:%S")
                print(f"[{now}] Initializing New Identity for {chat_id}...")
                
                # Railway সার্ভারে ক্রোমের সঠিক লোকেশন চিনিয়ে দেওয়া (Fix)
                driver = uc.Chrome(
                    options=options,
                    browser_executable_path="/usr/bin/google-chrome"
                )
                
                # ৩. লিঙ্কে প্রবেশ
                print(f"[{now}] Visiting Link: {url}")
                driver.get(url)
                
                # ৪. ১০ সেকেন্ড অপেক্ষা (আপনার অরিজিনাল কাউন্টডাউন লজিক)
                for second in range(10, 0, -1):
                    if not user_data.get(chat_id, {}).get('running', False): 
                        break
                    time.sleep(1)
                
                # ৫. সাকসেস কাউন্ট
                user_data[chat_id]['total_clicks'] += 1
                print(f"Success! Total Clicks for {chat_id}: {user_data[chat_id]['total_clicks']}")
                
            except Exception as e:
                print(f"Critical Error: {str(e)}")
            
            finally:
                if driver:
                    try:
                        driver.quit() # ব্রাউজার পুরোপুরি বন্ধ করা
                    except:
                        pass
                
                # একটি ব্রাউজার বন্ধ হওয়ার পর ২ সেকেন্ড গ্যাপ (আপনার লজিক)
                time.sleep(2)

    # থ্রেড সংখ্যা অনুযায়ী ইঞ্জিন স্টার্ট করা
    for i in range(threads_count):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        time.sleep(1) # পিসি/সার্ভার হ্যাং হওয়া রোধে ১ সেকেন্ড গ্যাপ

# --- টেলিগ্রাম ইন্টারফেস ডিজাইন (Buttons) ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    # ইউজার ডাটা ইনিশিয়ালাইজেশন
    user_data[chat_id] = {
        'running': False, 
        'url': '', 
        'threads': 5, # ডিফল্ট থ্রেড
        'total_clicks': 0
    }
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔗 Set URL")
    btn2 = types.KeyboardButton("🔢 Set Threads")
    btn3 = types.KeyboardButton("🚀 START ENGINE")
    btn4 = types.KeyboardButton("🛑 STOP ENGINE")
    btn5 = types.KeyboardButton("📊 Status")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
    
    welcome_text = (
        "🔥 *ADESTRA FAKE TRAFFIC SYSTEM*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Developed by: *MIZANUR RAHMAN*\n"
        "Status: Online & Ready\n\n"
        "নিচের বাটনগুলো ব্যবহার করে কন্ট্রোল করুন।"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        send_welcome(message)
        return

    text = message.text

    if text == "🔗 Set URL":
        msg = bot.send_message(chat_id, "আপনার Adestra Target URL-টি দিন:")
        bot.register_next_step_handler(msg, save_url)
    
    elif text == "🔢 Set Threads":
        msg = bot.send_message(chat_id, "থ্রেড সংখ্যা দিন (Railway-র জন্য ১-৩ এর মধ্যে রাখা ভালো):")
        bot.register_next_step_handler(msg, save_threads)

    elif text == "🚀 START ENGINE":
        target_url = user_data[chat_id]['url']
        if not target_url or "http" not in target_url:
            bot.send_message(chat_id, "❌ ভুল URL! আগে সঠিক লিঙ্ক সেট করুন।")
            return
        
        if user_data[chat_id]['running']:
            bot.send_message(chat_id, "⚠️ ইঞ্জিন অলরেডি রানিং আছে।")
            return

        bot.send_message(chat_id, f"🚀 ইঞ্জিন স্টার্ট হচ্ছে...\nThreads: {user_data[chat_id]['threads']}")
        run_automation(chat_id, target_url, user_data[chat_id]['threads'])

    elif text == "🛑 STOP ENGINE":
        user_data[chat_id]['running'] = False
        bot.send_message(chat_id, "🛑 ইঞ্জিন বন্ধ করার কমান্ড পাঠানো হয়েছে।")

    elif text == "📊 Status":
        status = "RUNNING 🟢" if user_data[chat_id]['running'] else "IDLE ⚪"
        report = (
            f"📊 *Current Status*\n"
            f"━━━━━━━━━━━━━━\n"
            f"Status: {status}\n"
            f"Total Clicks: {user_data[chat_id]['total_clicks']}\n"
            f"Active Threads: {user_data[chat_id]['threads']}\n"
            f"Target: {user_data[chat_id]['url']}"
        )
        bot.send_message(chat_id, report, parse_mode="Markdown")

def save_url(message):
    user_data[message.chat.id]['url'] = message.text
    bot.send_message(message.chat.id, "✅ URL সেভ হয়েছে।")

def save_threads(message):
    try:
        count = int(message.text)
        if count > 50: count = 50
        user_data[message.chat.id]['threads'] = count
        bot.send_message(message.chat.id, f"✅ থ্রেড সংখ্যা {count} এ সেট করা হয়েছে।")
    except:
        bot.send_message(message.chat.id, "❌ সঠিক সংখ্যা লিখুন।")

if __name__ == "__main__":
    print("Mizanur's Telegram Bot is starting...")
    bot.infinity_polling()
                    

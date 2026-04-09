import telebot
from telebot import types
import threading
import time
import random
from undetected_chromedriver import Chrome, ChromeOptions
from fake_useragent import UserAgent
from datetime import datetime

# --- কনফিগারেশন ---
API_TOKEN = '8615640384:AAHuqDZuv7zzxtvgUMwlAg6i1hrAHizcqC4'
bot = telebot.TeleBot(API_TOKEN)

# গ্লোবাল ভেরিয়েবল
user_data = {} # ইউজার ভিত্তিক সেটিংস সেভ রাখার জন্য
ua = UserAgent()

# --- মূল অটোমেশন ইঞ্জিন (অপরিবর্তিত লজিক) ---
def run_automation(chat_id, url, threads_count):
    user_data[chat_id]['running'] = True
    
    def worker():
        while user_data.get(chat_id, {}).get('running', False):
            driver = None
            try:
                options = ChromeOptions()
                current_ua = ua.random
                
                # আপনার অরিজিনাল আর্গুমেন্টস
                options.add_argument(f'--user-agent={current_ua}')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--incognito')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--headless') # সার্ভারে চালানোর জন্য হেডলেস জরুরি
                options.add_argument('--window-size=1280,720')
                
                # ব্রাউজার স্টার্ট
                driver = Chrome(options=options)
                
                now = datetime.now().strftime("%H:%M:%S")
                print(f"[{now}] Thread Active: Visiting {url}")
                
                driver.get(url)
                
                # ১০ সেকেন্ড অপেক্ষা (আপনার লজিক অনুযায়ী)
                for second in range(10, 0, -1):
                    if not user_data.get(chat_id, {}).get('running', False): break
                    time.sleep(1)
                
                user_data[chat_id]['total_clicks'] += 1
                
            except Exception as e:
                print(f"Error: {str(e)}")
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                time.sleep(2)

    # থ্রেড সংখ্যা অনুযায়ী লুপ চালানো
    for _ in range(threads_count):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        time.sleep(1)

# --- টেলিগ্রাম ইন্টারফেস ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat_id
    user_data[chat_id] = {'running': False, 'url': '', 'threads': 5, 'total_clicks': 0}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔗 Set URL", "🔢 Set Threads")
    markup.add("🚀 START ENGINE", "🛑 STOP ENGINE")
    markup.add("📊 Status")
    
    bot.reply_to(message, "ADESTRA FAKE TRAFFIC SYSTEM\nDeveloped by Mizanur Rahman\n\nনিচের বাটন ব্যবহার করে কন্ট্রোল করুন।", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat_id
    if chat_id not in user_data:
        user_data[chat_id] = {'running': False, 'url': '', 'threads': 5, 'total_clicks': 0}

    text = message.text

    if text == "🔗 Set URL":
        msg = bot.send_message(chat_id, "আপনার Adestra লিঙ্কটি দিন:")
        bot.register_next_step_handler(msg, save_url)
    
    elif text == "🔢 Set Threads":
        msg = bot.send_message(chat_id, "কতগুলো থ্রেড চালাতে চান? (১-১০ এর মধ্যে দিন):")
        bot.register_next_step_handler(msg, save_threads)

    elif text == "🚀 START ENGINE":
        if not user_data[chat_id]['url']:
            bot.send_message(chat_id, "❌ আগে URL সেট করুন!")
        elif user_data[chat_id]['running']:
            bot.send_message(chat_id, "⚠️ ইঞ্জিন অলরেডি চলছে।")
        else:
            bot.send_message(chat_id, f"✅ ইঞ্জিন চালু হচ্ছে...\nURL: {user_data[chat_id]['url']}\nThreads: {user_data[chat_id]['threads']}")
            run_automation(chat_id, user_data[chat_id]['url'], user_data[chat_id]['threads'])

    elif text == "🛑 STOP ENGINE":
        user_data[chat_id]['running'] = False
        bot.send_message(chat_id, "🛑 স্টপ কমান্ড পাঠানো হয়েছে। বর্তমান সেশনগুলো বন্ধ হচ্ছে...")

    elif text == "📊 Status":
        status = "RUNNING 🟢" if user_data[chat_id]['running'] else "IDLE ⚪"
        bot.send_message(chat_id, f"STATUS: {status}\nTotal Success: {user_data[chat_id]['total_clicks']}\nURL: {user_data[chat_id]['url']}")

def save_url(message):
    user_data[message.chat.id]['url'] = message.text
    bot.send_message(message.chat.id, "✅ URL সফলভাবে সেভ হয়েছে।")

def save_threads(message):
    try:
        count = int(message.text)
        user_data[message.chat.id]['threads'] = count
        bot.send_message(message.chat.id, f"✅ থ্রেড সেট করা হয়েছে: {count}")
    except:
        bot.send_message(message.chat.id, "❌ সঠিক সংখ্যা দিন।")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
                      

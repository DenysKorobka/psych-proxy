import os
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from fastapi import FastAPI
import uvicorn

# 1. Налаштування Telegram Бота
TOKEN = "8643334892:AAGtmsf-JlULGVSx2GqNKeks5Orjv47yFjM"

# ⚠️ ВАЖЛИВО: Вставте сюди своє посилання на міні-додаток (наприклад, з Netlify)
WEB_APP_URL = "https://denyskorobka.github.io/psych-miniapp/" 

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Відкрити додаток", web_app=WebAppInfo(url=WEB_APP_URL)))
    
    first_name = message.from_user.first_name or "клієнте"
    
    text = (f"Привіт, <b>{first_name}</b>! 👋\n\n"
            f"Я бот-асистент Олени Коваленко.\n\n"
            f"Увесь мій функціонал (запис на сесії, тести, корисні матеріали та AI-помічник) "
            f"тепер знаходиться у зручному міні-додатку.\n\n"
            f"Тисни кнопку нижче, щоб розпочати! 👇")
    
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_other_messages(message):
    # Якщо людина пише щось інше, направляємо її в додаток
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Відкрити додаток", web_app=WebAppInfo(url=WEB_APP_URL)))
    bot.send_message(
        message.chat.id, 
        "Щоб скористатися всіма функціями, просто відкрий наш міні-додаток 👇", 
        reply_markup=markup
    )

def run_bot():
    print("Запуск Telegram бота...")
    bot.infinity_polling()

# 2. Налаштування FastAPI (щоб Railway не видавав помилку сервера)
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Bot is running!"}

@app.on_event("startup")
def on_startup():
    # Запускаємо бота паралельно з веб-сервером
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

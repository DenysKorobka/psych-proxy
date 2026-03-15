import os
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from fastapi import FastAPI
import uvicorn

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEB_APP_URL = "https://denyskorobka.github.io/psych-miniapp/"
APP_VERSION = "BOT_VERSION_2026_03_15_21_00"

bot = telebot.TeleBot(TOKEN)
app = FastAPI()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, f"НОВИЙ КОД ПРАЦЮЄ ✅ {APP_VERSION}")

def run_bot():
    print("Запуск Telegram бота...")
    bot.infinity_polling(skip_pending=True)

@app.get("/")
def read_root():
    return {"status": "Bot is running!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/debug")
def debug():
    me = bot.get_me()
    return {
        "version": APP_VERSION,
        "bot_username": me.username,
        "bot_id": me.id
    }

@app.on_event("startup")
def on_startup():
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

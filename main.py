import os
import threading
import telebot
from telebot.types import ReplyKeyboardRemove
from fastapi import FastAPI
import uvicorn

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
bot = telebot.TeleBot(TOKEN)
app = FastAPI()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "НОВИЙ СТАРТ 999 ✅",
        reply_markup=ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    bot.send_message(
        message.chat.id,
        "БУДЬ-ЯКЕ ПОВІДОМЛЕННЯ 888",
        reply_markup=ReplyKeyboardRemove()
    )

def run_bot():
    print("Запуск Telegram бота...")
    bot.infinity_polling(skip_pending=True)

@app.get("/")
def root():
    return {"ok": True}

@app.get("/debug")
def debug():
    me = bot.get_me()
    return {
        "bot_username": me.username,
        "bot_id": me.id,
        "version": "hard-reset"
    }

@app.on_event("startup")
def startup():
    threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

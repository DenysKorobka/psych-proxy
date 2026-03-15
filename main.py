import os
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from fastapi import FastAPI
import uvicorn

# 1. Налаштування Telegram Бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Посилання на міні-додаток
WEB_APP_URL = "https://denyskorobka.github.io/psych-miniapp/"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "Протестувати бота",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )

    first_name = message.from_user.first_name or "друже"

    text = (
        f"Привіт, <b>{first_name}</b>! 👋\n\n"
        f"Це <b>демо AI чат-боту</b>, у якому можна протестувати різні функції "
        f"для автоматизації взаємодії з клієнтами.\n\n"
        f"У міні-додатку ти зможеш подивитися, як працюють:\n"
        f"• AI-помічник\n"
        f"• запис клієнтів\n"
        f"• інтерактивні сценарії\n"
        f"• автоматизація комунікації\n\n"
        f"Натисни кнопку нижче, щоб <b>відкрити додаток і протестувати функціонал</b> 👇"
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_all_other_messages(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "🚀 Відкрити додаток",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )

    bot.send_message(
        message.chat.id,
        "Щоб протестувати можливості цього чат-боту, відкрий міні-додаток 👇",
        reply_markup=markup
    )

def run_bot():
    print("Запуск Telegram бота...")
    bot.infinity_polling(skip_pending=True)

# 2. Налаштування FastAPI (щоб Railway не видавав помилку сервера)
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Bot is running!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
def on_startup():
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

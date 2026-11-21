import os
import re
import threading
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.get("/healthz")
def health():
    return "Bot is running!", 200

@bot.message_handler(commands=["start"])
def start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            "TikTok Official Website",
            url="https://www.tiktok.com/"
        )
    )

    bot.reply_to(
        message,
        "👋 Welcome to TikTok Passkey Checker!\n\n"
        "Send your TikTok username to check its format.\n\n"
        "⚠️ Public username lookup cannot reveal "
        "whether an account has a Passkey.\n\n"
        "Never share your password or OTP.",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda m: True)
def check_username(message):
    username = message.text.strip().lstrip("@")

    if not re.fullmatch(r"[A-Za-z0-9._]{2,24}", username):
        bot.reply_to(message, "❌ Invalid username format.")
        return

    bot.reply_to(
        message,
        f"👤 Username: @{username}\n\n"
        "✅ Username format looks valid.\n\n"
        "🔐 Passkey Status: Cannot be verified publicly.\n\n"
        "Check your Passkey in TikTok Settings > "
        "Security & permissions > Passkey.\n\n"
        "This bot does not access passwords or OTPs."
    )

def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0",
            port=int(os.environ.get("PORT", 10000)))

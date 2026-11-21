
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

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            "🔐 TikTok Security Settings",
            url="https://www.tiktok.com/"
        ),
        InlineKeyboardButton("ℹ️ About Bot", callback_data="about"),
        InlineKeyboardButton("❓ Help", callback_data="help")
    )
    return keyboard

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 Welcome to TikTok Passkey Checker!\n\n"
        "Send your TikTok username to check its format.\n\n"
        "🔐 Passkey Status Options:\n"
        "🟢 ENABLED\n"
        "🔴 DISABLED\n"
        "🟡 UNKNOWN\n\n"
        "Note: Public username lookup cannot verify "
        "real Passkey status.\n\n"
        "Never share your password or OTP.",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.reply_to(
        message,
        "📌 How to use:\n\n"
        "1. Send a TikTok username.\n"
        "2. Bot checks username format.\n"
        "3. Passkey status is shown as UNKNOWN "
        "when verification is unavailable.\n\n"
        "Check your actual Passkey in TikTok settings."
    )

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    if call.data == "about":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🤖 TikTok Passkey Checker\n"
            "Version 2.0\n\n"
            "This bot checks username format only. "
            "It cannot access private TikTok security data."
        )
    elif call.data == "help":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "Send a TikTok username, with or without @."
        )

@bot.message_handler(func=lambda m: bool(m.text))
def check_username(message):
    username = message.text.strip().lstrip("@")

    if not re.fullmatch(r"[A-Za-z0-9._]{2,24}", username):
        bot.reply_to(
            message,
            "❌ Invalid username format.\n"
            "Please enter a valid username."
        )
        return

    bot.reply_to(
        message,
        f"👤 Username: @{username}\n\n"
        "✅ Username Format: Valid\n\n"
        "🔐 Passkey Status: 🟡 UNKNOWN\n\n"
        "TikTok does not provide public username-based "
        "Passkey verification.\n\n"
        "To check your real Passkey:\n"
        "Open TikTok → Profile → Menu → Settings and "
        "privacy → Account → Passkey.\n\n"
        "🔒 Your password and OTP are never requested.",
        reply_markup=main_menu()
    )

def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )

import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Update
from telegram.ext import Application, CommandHandler, ContextTypes

import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not configured")
    
WEBAPP_URL = os.environ.get(
    "WEBAPP_URL",
    "https://etntestbot.netlify.app"
).strip()

async def open_app(update: Update, context: ContextTypes.DEFAULT_TYPE, pts=False):
    if not WEBAPP_URL.startswith("https://"):
        await update.message.reply_text(
            "Бот запущен, но WEBAPP_URL не настроен.\n"
            "Нужен публичный HTTPS-адрес (например, через Cloudflare Tunnel)."
        )
        return
    keyboard = [[InlineKeyboardButton(
        "Открыть ETN RAPIRA ONLINE",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )]]
    message = ("Открой рейтинг PTS ETN: очки за победы/поражения, убийства, ассисты и MVP.\n"
               "В рейтинге учитываются подтверждённые турнирные матчи.") if pts else (
        "Добро пожаловать в ETN RAPIRA ONLINE!\nНажми кнопку ниже, чтобы открыть турнирную платформу.")
    if pts:
        keyboard = [[InlineKeyboardButton("Открыть ETN · PTS", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_app(update, context, pts=False)

async def pts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_app(update, context, pts=True)

def main():
    if not BOT_TOKEN:
        raise SystemExit("Укажи BOT_TOKEN в переменных окружения.")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pts", pts_command))
    print("ETN Telegram bot started. Stop with Ctrl+C.")
    app.run_polling()

if __name__ == "__main__":
    main()

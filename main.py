import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from birthday import (
    BIRTHDAY_BUTTON,
    birthday_start,
    birthday_message_handler,
)


# =========================
# CONFIG
# =========================

TOKEN = os.getenv("TOKEN")

DEVELOPER_ID = os.getenv("DEVELOPER_ID", "").strip()
DEVELOPER_USERNAME = os.getenv(
    "DEVELOPER_USERNAME",
    "@Do*x*Die"
).strip()

PORT = int(os.getenv("PORT", "10000"))

if not TOKEN:
    raise ValueError("TOKEN environment variable not found!")


# =========================
# MAIN MENU
# =========================

START_BUTTON = "🏠 Start"
DEVELOPER_BUTTON = "👨‍💻 Developer"

MAIN_KEYBOARD = [
    [START_BUTTON],
    [BIRTHDAY_BUTTON],
    [DEVELOPER_BUTTON],
]

MAIN_MARKUP = ReplyKeyboardMarkup(
    MAIN_KEYBOARD,
    resize_keyboard=True
)


# =========================
# RENDER HEALTH SERVER
# =========================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ["/", "/health"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(
                b"Birthday Calculator Bot is running!"
            )
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def run_health_server():
    server = HTTPServer(
        ("0.0.0.0", PORT),
        HealthHandler
    )
    server.serve_forever()


# =========================
# START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    user = update.effective_user

    name = user.first_name or "Friend"

    text = (
        f"🎂 Hello {name}!\n\n"
        "Welcome to the Birthday Calculator Bot 🎉\n\n"
        "Here you can calculate:\n"
        "🎂 Your exact age\n"
        "📅 Next birthday\n"
        "⏳ Birthday countdown\n"
        "♈ Western Zodiac\n"
        "🐉 Chinese Zodiac\n"
        "🔢 Life Path Number\n"
        "🌙 Moon phase\n"
        "❤️ Estimated heartbeats\n"
        "😴 Estimated sleep\n"
        "🌍 Earth revolutions\n"
        "📊 Life statistics\n"
        "🎯 Age milestones\n"
        "🖼 Birthday Card\n\n"
        "Choose an option below."
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_MARKUP
    )


# =========================
# DEVELOPER
# =========================

async def developer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    developer_id_text = (
        DEVELOPER_ID
        if DEVELOPER_ID
        else "Not provided"
    )

    text = (
        "👨‍💻 Developer Information\n\n"
        "👤 Name: MASTERMIND\n"
        f"📱 Telegram: {DEVELOPER_USERNAME}\n"
        f"🆔 Telegram ID: {developer_id_text}\n\n"
        "💻 Birthday Calculator Bot"
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_MARKUP
    )


# =========================
# TEXT ROUTER
# =========================

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    if text == START_BUTTON:
        await start(update, context)
        return

    if text == DEVELOPER_BUTTON:
        await developer(update, context)
        return

    if text == BIRTHDAY_BUTTON:
        await birthday_start(update, context)
        return

    await birthday_message_handler(update, context)


# =========================
# MAIN
# =========================

def main():

    # Render health server
    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True
    )

    health_thread.start()

    # Telegram bot
    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", start)
    )

    application.add_handler(
        CommandHandler(
            "cancel",
            birthday_start
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_router
        )
    )

    print("🎂 Birthday Calculator Bot started!")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()

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


# ============================================================
# CONFIGURATION
# ============================================================

TOKEN = os.getenv("TOKEN")

DEVELOPER_ID = os.getenv("DEVELOPER_ID", "").strip()

DEVELOPER_USERNAME = os.getenv(
    "DEVELOPER_USERNAME",
    "@Do*x*Die"
).strip()

PORT = int(os.getenv("PORT", "10000"))

if not TOKEN:
    raise ValueError(
        "TOKEN environment variable is missing!"
    )


# ============================================================
# MAIN MENU
# ============================================================

START_BUTTON = "🏠 Start"
DEVELOPER_BUTTON = "👨‍💻 Developer"

MAIN_KEYBOARD = [
    [START_BUTTON],
    [BIRTHDAY_BUTTON],
    [DEVELOPER_BUTTON],
]

MAIN_MARKUP = ReplyKeyboardMarkup(
    MAIN_KEYBOARD,
    resize_keyboard=True,
)


# ============================================================
# RENDER HEALTH SERVER
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ["/", "/health"]:

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

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

    print(
        f"🌐 Health server running on port {PORT}"
    )

    server.serve_forever()


# ============================================================
# /START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    user = update.effective_user

    name = (
        user.first_name
        if user and user.first_name
        else "Friend"
    )

    text = (
        f"🎂 Hello {name}!\n\n"

        "✨ Welcome to Birthday Calculator Bot!\n\n"

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
        "📅 Day milestones\n"
        "🖼️ Birthday Card\n\n"

        "👇 Choose an option below."
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_MARKUP
    )


# ============================================================
# DEVELOPER
# ============================================================

async def developer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    developer_id = (
        DEVELOPER_ID
        if DEVELOPER_ID
        else "Not provided"
    )

    text = (
        "👨‍💻 Developer Information\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        "👤 Name: MASTERMIND\n"
        f"📱 Telegram: {DEVELOPER_USERNAME}\n"
        f"🆔 Telegram ID: {developer_id}\n\n"

        "🤖 Bot: Birthday Calculator Bot\n"
        "💻 Developed by MASTERMIND"
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_MARKUP
    )


# ============================================================
# MESSAGE ROUTER
# ============================================================

async def message_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    if not update.message.text:
        return

    text = update.message.text.strip()

    # Main menu
    if text == START_BUTTON:
        await start(update, context)
        return

    # Developer
    if text == DEVELOPER_BUTTON:
        await developer(update, context)
        return

    # Birthday calculator
    if text == BIRTHDAY_BUTTON:
        await birthday_start(update, context)
        return

    # Birthday calculator internal handler
    await birthday_message_handler(
        update,
        context
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # Start Render health server
    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True
    )

    health_thread.start()

    # Build Telegram application
    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    # Commands
    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            start
        )
    )

    application.add_handler(
        CommandHandler(
            "cancel",
            birthday_start
        )
    )

    # Text messages
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_router
        )
    )

    print(
        "🎂 Birthday Calculator Bot started successfully!"
    )

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()

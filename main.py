import os
import threading
from pathlib import Path
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    MenuButtonWebApp,
    WebAppInfo,
)
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

from date_calculator import (
    DATE_CALCULATOR_BUTTON,
    date_calculator_start,
    date_calculator_handler,
    is_date_calculator_active,
)


# =========================================================
# CONFIG
# =========================================================

TOKEN = os.getenv("BOT_TOKEN")

RENDER_URL = os.getenv(
    "RENDER_URL",
    "https://cracker-birthday-calculator.onrender.com"
)

DEVELOPER_NAME = "MASTERMIND"
DEVELOPER_USERNAME = "@Do_x_Die"
DEVELOPER_ID = os.getenv("DEVELOPER_ID", "")

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

if not TOKEN:
    raise ValueError(
        "BOT_TOKEN environment variable is missing!"
    )


# =========================================================
# MENU
# =========================================================

START_BUTTON = "🏠 Start"
DEVELOPER_BUTTON = "👨‍💻 Developer"

MAIN_KEYBOARD = [
    [START_BUTTON],
    [BIRTHDAY_BUTTON],
    [DATE_CALCULATOR_BUTTON],
    [DEVELOPER_BUTTON],
]

MAIN_MARKUP = ReplyKeyboardMarkup(
    MAIN_KEYBOARD,
    resize_keyboard=True
)


# =========================================================
# START
# =========================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.pop("date_calc_state", None)
    context.user_data.pop("date_calc_first_date", None)
    context.user_data.pop("date_calc_second_date", None)

    await update.message.reply_text(
        "🚀 Welcome to Calculator Universe!\n\n"
        "🎂 Birthday Calculator\n"
        "📆 Date Difference Calculator\n\n"
        "Choose an option below.",
        reply_markup=MAIN_MARKUP
    )


# =========================================================
# HELP
# =========================================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📚 Help\n\n"
        "/start - Main menu\n"
        "/help - Help\n"
        "/cancel - Cancel calculation",
        reply_markup=MAIN_MARKUP
    )


# =========================================================
# CANCEL
# =========================================================

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.pop("date_calc_state", None)
    context.user_data.pop("date_calc_first_date", None)
    context.user_data.pop("date_calc_second_date", None)

    await update.message.reply_text(
        "❌ Calculation cancelled.",
        reply_markup=MAIN_MARKUP
    )


# =========================================================
# DEVELOPER
# =========================================================

async def developer_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    developer_id = DEVELOPER_ID or "Not provided"

    await update.message.reply_text(
        "👨‍💻 DEVELOPER\n\n"
        f"Name: {DEVELOPER_NAME}\n"
        f"Telegram: {DEVELOPER_USERNAME}\n"
        f"ID: {developer_id}\n\n"
        "⚡ Calculator Universe\n"
        "Powered by MASTERMIND.",
        reply_markup=MAIN_MARKUP
    )


# =========================================================
# MESSAGE ROUTER
# =========================================================

async def text_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = update.message.text

    if text == START_BUTTON:
        await start_command(update, context)
        return

    if text == BIRTHDAY_BUTTON:
        await birthday_start(update, context)
        return

    if text == DATE_CALCULATOR_BUTTON:
        await date_calculator_start(update, context)
        return

    if text == DEVELOPER_BUTTON:
        await developer_handler(update, context)
        return

    if is_date_calculator_active(context):
        await date_calculator_handler(update, context)
        return

    await birthday_message_handler(update, context)


# =========================================================
# TELEGRAM WEB APP MENU
# =========================================================

async def setup_bot_menu(application: Application):

    await application.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🌐 Open Website",
            web_app=WebAppInfo(
                url=RENDER_URL
            )
        )
    )


# =========================================================
# WEB SERVER
# =========================================================

class WebHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

    def serve_file(self, filename, content_type):

        file_path = WEB_DIR / filename

        if not file_path.exists():
            self.send_error(404, "File not found")
            return

        try:

            data = file_path.read_bytes()

            self.send_response(200)

            self.send_header(
                "Content-Type",
                content_type
            )

            self.send_header(
                "Content-Length",
                str(len(data))
            )

            self.send_header(
                "Cache-Control",
                "no-cache, no-store, must-revalidate"
            )

            self.end_headers()

            self.wfile.write(data)

        except Exception:
            self.send_error(
                500,
                "Internal server error"
            )

    def do_GET(self):

        path = urlparse(self.path).path

        if path in ["/", "/index.html"]:

            self.serve_file(
                "index.html",
                "text/html; charset=utf-8"
            )

            return

        if path == "/style.css":

            self.serve_file(
                "style.css",
                "text/css; charset=utf-8"
            )

            return

        if path == "/script.js":

            self.serve_file(
                "script.js",
                "application/javascript; charset=utf-8"
            )

            return

        if path == "/health":

            data = b"OK"

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(len(data))
            )

            self.end_headers()

            self.wfile.write(data)

            return

        self.send_error(
            404,
            "Not Found"
        )


# =========================================================
# WEB SERVER THREAD
# =========================================================

def run_web_server():

    port = int(
        os.getenv(
            "PORT",
            "10000"
        )
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        WebHandler
    )

    print(
        f"🌐 Website running on port {port}"
    )

    server.serve_forever()


# =========================================================
# MAIN
# =========================================================

def main():

    print("================================")
    print("🚀 CALCULATOR UNIVERSE")
    print("================================")
    print(f"🌐 Website: {RENDER_URL}")
    print("🤖 Bot: @cracker_team_05_bot")
    print("👨‍💻 Developer: @Do_x_Die")
    print("================================")

    application = (
        Application.builder()
        .token(TOKEN)
        .post_init(setup_bot_menu)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start_command
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    application.add_handler(
        CommandHandler(
            "cancel",
            cancel_command
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_router
        )
    )

    web_thread = threading.Thread(
        target=run_web_server,
        daemon=True
    )

    web_thread.start()

    print("🤖 Starting Telegram polling...")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()

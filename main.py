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
# CONFIGURATION
# =========================================================

TOKEN = os.getenv("BOT_TOKEN")

RENDER_URL = os.getenv(
    "RENDER_URL",
    "https://cracker-birthday-calculator.onrender.com"
)

DEVELOPER_NAME = "MASTERMIND"
DEVELOPER_USERNAME = "@Do*x*Die"
DEVELOPER_ID = os.getenv("DEVELOPER_ID", "")

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"


if not TOKEN:
    raise ValueError(
        "BOT_TOKEN environment variable is missing!"
    )


# =========================================================
# MAIN KEYBOARD
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
# START COMMAND
# =========================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data.pop(
        "date_calc_state",
        None
    )

    context.user_data.pop(
        "date_calc_first_date",
        None
    )

    context.user_data.pop(
        "date_calc_second_date",
        None
    )

    await update.message.reply_text(
        "🚀 Welcome to Calculator Universe!\n\n"
        "🎂 Birthday Calculator\n"
        "📆 Date Difference Calculator\n\n"
        "Choose a calculator from the menu below.",
        reply_markup=MAIN_MARKUP
    )


# =========================================================
# HELP COMMAND
# =========================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "📚 Help\n\n"
        "/start - Open main menu\n"
        "/help - Show help\n"
        "/cancel - Cancel current calculation\n\n"
        "Use the buttons below to start a calculator.",
        reply_markup=MAIN_MARKUP
    )


# =========================================================
# CANCEL COMMAND
# =========================================================

async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data.pop(
        "date_calc_state",
        None
    )

    context.user_data.pop(
        "date_calc_first_date",
        None
    )

    context.user_data.pop(
        "date_calc_second_date",
        None
    )

    await update.message.reply_text(
        "❌ Current calculation cancelled.\n\n"
        "You are back in the main menu.",
        reply_markup=MAIN_MARKUP
    )


# =========================================================
# DEVELOPER
# =========================================================

async def developer_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    developer_id = (
        DEVELOPER_ID
        if DEVELOPER_ID
        else "Not provided"
    )

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

    # Main menu
    if text == START_BUTTON:
        await start_command(update, context)
        return

    # Birthday Calculator
    if text == BIRTHDAY_BUTTON:
        await birthday_start(update, context)
        return

    # Date Difference Calculator
    if text == DATE_CALCULATOR_BUTTON:
        await date_calculator_start(update, context)
        return

    # Developer
    if text == DEVELOPER_BUTTON:
        await developer_handler(update, context)
        return

    # Date calculator active state
    if is_date_calculator_active(context):
        await date_calculator_handler(update, context)
        return

    # Birthday calculator fallback
    await birthday_message_handler(update, context)


# =========================================================
# TELEGRAM MENU BUTTON
# =========================================================

async def setup_bot_menu(
    application: Application
):
    await application.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🌐 Open / Wake Bot",
            web_app=WebAppInfo(
                url=RENDER_URL
            )
        )
    )


# =========================================================
# WEBSITE SERVER
# =========================================================

class HealthHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Keep Render logs clean
        return

    def send_file(
        self,
        file_path: Path,
        content_type: str
    ):
        if not file_path.exists() or not file_path.is_file():
            self.send_error(
                404,
                "File not found"
            )
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
                "no-cache"
            )

            self.end_headers()

            self.wfile.write(data)

        except Exception:
            self.send_error(
                500,
                "Internal Server Error"
            )

    def do_GET(self):

        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # -------------------------------------------------
        # HOME PAGE
        # -------------------------------------------------

        if path in ["/", "/index.html"]:

            self.send_file(
                WEB_DIR / "index.html",
                "text/html; charset=utf-8"
            )

            return

        # -------------------------------------------------
        # CSS
        # -------------------------------------------------

        if path == "/style.css":

            self.send_file(
                WEB_DIR / "style.css",
                "text/css; charset=utf-8"
            )

            return

        # -------------------------------------------------
        # JAVASCRIPT
        # -------------------------------------------------

        if path == "/script.js":

            self.send_file(
                WEB_DIR / "script.js",
                "application/javascript; charset=utf-8"
            )

            return

        # -------------------------------------------------
        # HEALTH CHECK
        # -------------------------------------------------

        if path == "/health":

            response = b"OK"

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(len(response))
            )

            self.end_headers()

            self.wfile.write(response)

            return

        # -------------------------------------------------
        # 404
        # -------------------------------------------------

        self.send_error(
            404,
            "Page not found"
        )


# =========================================================
# RUN WEBSITE SERVER
# =========================================================

def run_health_server():

    port = int(
        os.getenv(
            "PORT",
            "10000"
        )
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    print(
        f"🌐 Website server running on port {port}"
    )

    server.serve_forever()


# =========================================================
# MAIN
# =========================================================

def main():

    print("🚀 Starting Calculator Universe...")
    print(
        f"🌐 Website: {RENDER_URL}"
    )
    print(
        f"🤖 Telegram: @cracker_team_05_bot"
    )

    # ---------------------------------------------
    # Telegram Application
    # ---------------------------------------------

    application = (
        Application.builder()
        .token(TOKEN)
        .post_init(setup_bot_menu)
        .build()
    )

    # ---------------------------------------------
    # Commands
    # ---------------------------------------------

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

    # ---------------------------------------------
    # Text Messages
    # ---------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_router
        )
    )

    # ---------------------------------------------
    # Website / Health Server
    # ---------------------------------------------

    server_thread = threading.Thread(
        target=run_health_server,
        daemon=True
    )

    server_thread.start()

    # ---------------------------------------------
    # Start Telegram Bot
    # ---------------------------------------------

    print("🤖 Telegram bot is starting...")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()

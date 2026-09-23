
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

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

# IMPORTANT:
# Your birthday.py uses birthday_message_handler,
# NOT birthday_handler.
from birthday import (
    birthday_message_handler,
    birthday_start,
)


# ============================================================
# CONFIG
# ============================================================

TOKEN = os.getenv("TOKEN")

DEVELOPER_ID = os.getenv(
    "DEVELOPER_ID",
    ""
).strip()

DEVELOPER_USERNAME = os.getenv(
    "DEVELOPER_USERNAME",
    "@Do*x*Die"
).strip()

PORT = int(
    os.getenv(
        "PORT",
        "10000"
    )
)

# Your Render URL
RENDER_URL = (
    "https://cracker-birthday-calculator.onrender.com"
)


if not TOKEN:
    raise ValueError(
        "TOKEN environment variable is missing!"
    )


# ============================================================
# MAIN MENU
# ============================================================

START_BUTTON = "🏠 Start"
BIRTHDAY_BUTTON = "🎂 Birthday Calculator"
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


# ============================================================
# TELEGRAM TOP MENU
# ============================================================
#
# Telegram-এর ☰ Menu-এর ভিতরে:
#
# 🌐 Open / Wake Bot
#
# এই button-এ click করলে Render URL খুলবে।
# ============================================================

async def setup_bot_menu(
    application: Application
):

    try:

        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="🌐 Open / Wake Bot",
                web_app=WebAppInfo(
                    url=RENDER_URL
                )
            )
        )

        print(
            "✅ Telegram ☰ Menu configured."
        )

    except Exception as error:

        print(
            "⚠️ Could not configure Telegram menu:",
            error
        )


# ============================================================
# RENDER HEALTH SERVER
# ============================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <title>
        Birthday Calculator Bot
    </title>

    <style>

        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px 20px;
            background: #f5f5f5;
        }

        .box {
            max-width: 600px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow:
                0 4px 20px
                rgba(0, 0, 0, 0.08);
        }

        h1 {
            margin-bottom: 10px;
        }

        p {
            color: #555;
        }

    </style>
</head>

<body>

    <div class="box">

        <h1>
            🎂 Birthday Calculator Bot
        </h1>

        <p>
            🟢 Bot service is running.
        </p>

        <p>
            You can return to Telegram
            and use the bot.
        </p>

    </div>

</body>
</html>
"""

        body = html.encode(
            "utf-8"
        )

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format,
        *args
    ):
        return


def start_health_server():

    server = HTTPServer(
        (
            "0.0.0.0",
            PORT
        ),
        HealthHandler
    )

    print(
        f"🌐 Health server running on port {PORT}"
    )

    server.serve_forever()


# ============================================================
# /START
# ============================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    user = update.effective_user

    first_name = (
        user.first_name
        if user and user.first_name
        else "there"
    )

    text = (
        f"🎉 Hello {first_name}!\n\n"

        "🎂 Welcome to Birthday "
        "Calculator Bot!\n\n"

        "Calculate your:\n"
        "📅 Age\n"
        "🎂 Next Birthday\n"
        "⏳ Birthday Countdown\n"
        "♈ Zodiac\n"
        "🔢 Life Path Number\n"
        "📊 Life Statistics\n"
        "🎯 Age Milestones\n"
        "🖼️ Birthday Card\n\n"

        "👇 Choose an option below."
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_MARKUP
    )


# ============================================================
# /HELP
# ============================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = (
        "📖 Birthday Calculator Bot\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        "🏠 /start\n"
        "Open the main menu.\n\n"

        "🎂 Birthday Calculator\n"
        "Calculate your birthday information.\n\n"

        "❌ /cancel\n"
        "Cancel the current calculation.\n\n"

        "📖 /help\n"
        "Show this help message.\n\n"

        "☰ Telegram Menu\n"
        "Use the Telegram ☰ Menu at the "
        "top of the chat to open the Render "
        "service."
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_MARKUP
    )


# ============================================================
# /CANCEL
# ============================================================

async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Calculation cancelled.\n\n"
        "🏠 Back to main menu.",
        reply_markup=MAIN_MARKUP
    )


# ============================================================
# DEVELOPER
# ============================================================

async def developer_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = (
        "👨‍💻 DEVELOPER\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        "Name: MASTERMIND\n"
        f"Telegram: {DEVELOPER_USERNAME}\n"
    )

    if DEVELOPER_ID:

        text += (
            f"Telegram ID: "
            f"{DEVELOPER_ID}\n"
        )

    else:

        text += (
            "Telegram ID: Not provided\n"
        )

    text += (
        "\n🎂 Birthday Calculator Bot"
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_MARKUP
    )


# ============================================================
# TEXT ROUTER
# ============================================================

async def text_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if (
        not update.message
        or not update.message.text
    ):
        return

    text = update.message.text.strip()

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    if text == START_BUTTON:

        await start_command(
            update,
            context
        )

        return

    # --------------------------------------------------------
    # BIRTHDAY CALCULATOR
    # --------------------------------------------------------

    if text == BIRTHDAY_BUTTON:

        await birthday_start(
            update,
            context
        )

        return

    # --------------------------------------------------------
    # DEVELOPER
    # --------------------------------------------------------

    if text == DEVELOPER_BUTTON:

        await developer_command(
            update,
            context
        )

        return

    # --------------------------------------------------------
    # BIRTHDAY CALCULATOR HANDLER
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # This matches the actual function
    # inside your birthday.py:
    #
    # birthday_message_handler
    # --------------------------------------------------------

    await birthday_message_handler(
        update,
        context
    )


# ============================================================
# ERROR HANDLER
# ============================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    print(
        "⚠️ Telegram bot error:",
        context.error
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "🚀 Starting Birthday Calculator Bot..."
    )

    # --------------------------------------------------------
    # START RENDER HTTP SERVER
    # --------------------------------------------------------

    health_thread = Thread(
        target=start_health_server,
        daemon=True
    )

    health_thread.start()

    # --------------------------------------------------------
    # BUILD TELEGRAM APPLICATION
    # --------------------------------------------------------

    application = (
        Application.builder()
        .token(TOKEN)
        .post_init(setup_bot_menu)
        .build()
    )

    # --------------------------------------------------------
    # COMMANDS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # TEXT MESSAGES
    # --------------------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            text_router
        )
    )

    # --------------------------------------------------------
    # ERROR HANDLER
    # --------------------------------------------------------

    application.add_error_handler(
        error_handler
    )

    print(
        "🤖 Birthday Calculator Bot is running!"
    )

    print(
        "☰ Telegram Menu:"
        " 🌐 Open / Wake Bot"
    )

    print(
        f"🌐 Render URL: {RENDER_URL}"
    )

    # --------------------------------------------------------
    # START POLLING
    # --------------------------------------------------------

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

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

# ============================================================
# BIRTHDAY CALCULATOR
# ============================================================

from birthday import (
    birthday_message_handler,
    birthday_start,
)

# ============================================================
# DATE DIFFERENCE CALCULATOR
# ============================================================

from date_calculator import (
    DATE_CALCULATOR_BUTTON,
    date_calculator_start,
    date_calculator_handler,
    is_date_calculator_active,
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


# ============================================================
# MAIN KEYBOARD
# ============================================================

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


# ============================================================
# TELEGRAM TOP MENU
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
            📆 Date Difference Calculator
            is also available.
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

        "🤖 Welcome to Birthday "
        "Calculator Bot!\n\n"

        "Available features:\n\n"

        "🎂 Birthday Calculator\n"
        "Calculate your age, birthday, zodiac, "
        "life statistics and more.\n\n"

        "📆 Date Difference Calculator\n"
        "Compare any two dates and get days, "
        "weeks, hours, minutes, seconds, "
        "calendar difference and countdown.\n\n"

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
        "📖 CALCULATOR BOT HELP\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        "🏠 /start\n"
        "Open the main menu.\n\n"

        "🎂 Birthday Calculator\n"
        "Calculate age, next birthday, "
        "countdown, zodiac, life path, "
        "life statistics and milestones.\n\n"

        "📆 Date Difference Calculator\n"
        "Enter two dates and get:\n"
        "• Weekday of both dates\n"
        "• Total days\n"
        "• Weeks + days\n"
        "• Years + months + days\n"
        "• Total hours\n"
        "• Total minutes\n"
        "• Total seconds\n"
        "• Countdown from today\n"
        "• Leap year information\n"
        "• Leap days\n"
        "• Day of year\n"
        "• Weekend information\n"
        "• Much more\n\n"

        "❌ /cancel\n"
        "Cancel the current calculation.\n\n"

        "📖 /help\n"
        "Show this help message."
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
        "\n🎂 Birthday Calculator Bot\n"
        "📆 Date Difference Calculator"
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


    # ========================================================
    # START BUTTON
    # ========================================================

    if text == START_BUTTON:

        await start_command(
            update,
            context
        )

        return


    # ========================================================
    # BIRTHDAY BUTTON
    # ========================================================

    if text == BIRTHDAY_BUTTON:

        await birthday_start(
            update,
            context
        )

        return


    # ========================================================
    # DATE DIFFERENCE BUTTON
    # ========================================================

    if text == DATE_CALCULATOR_BUTTON:

        await date_calculator_start(
            update,
            context
        )

        return


    # ========================================================
    # DEVELOPER BUTTON
    # ========================================================

    if text == DEVELOPER_BUTTON:

        await developer_command(
            update,
            context
        )

        return


    # ========================================================
    # DATE CALCULATOR ACTIVE
    # ========================================================

    if is_date_calculator_active(
        context
    ):

        await date_calculator_handler(
            update,
            context
        )

        return


    # ========================================================
    # BIRTHDAY CALCULATOR
    # ========================================================

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
    # Render health server
    # --------------------------------------------------------

    health_thread = Thread(
        target=start_health_server,
        daemon=True
    )

    health_thread.start()


    # --------------------------------------------------------
    # Telegram Application
    # --------------------------------------------------------

    application = (
        Application.builder()
        .token(TOKEN)
        .post_init(setup_bot_menu)
        .build()
    )


    # --------------------------------------------------------
    # Commands
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
    # Text messages
    # --------------------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            text_router
        )
    )


    # --------------------------------------------------------
    # Error handler
    # --------------------------------------------------------

    application.add_error_handler(
        error_handler
    )


    # --------------------------------------------------------
    # Start
    # --------------------------------------------------------

    print(
        "🤖 Birthday Calculator Bot is running!"
    )

    print(
        "📆 Date Difference Calculator enabled!"
    )

    print(
        "☰ Telegram Menu:"
        " 🌐 Open / Wake Bot"
    )

    print(
        f"🌐 Render URL: {RENDER_URL}"
    )


    # --------------------------------------------------------
    # Polling
    # --------------------------------------------------------

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()


import os
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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

from birthday import birthday_handler, birthday_start


# =========================================================
# CONFIG
# =========================================================

TOKEN = os.getenv("TOKEN")

DEVELOPER_ID = os.getenv("DEVELOPER_ID", "").strip()
DEVELOPER_USERNAME = os.getenv(
    "DEVELOPER_USERNAME",
    "@Do*x*Die"
).strip()

PORT = int(os.getenv("PORT", "10000"))

# Your Render service URL
RENDER_URL = "https://cracker-birthday-calculator.onrender.com"


if not TOKEN:
    raise ValueError("TOKEN environment variable is missing!")


# =========================================================
# MAIN MENU BUTTONS
# =========================================================

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


# =========================================================
# TELEGRAM MENU BUTTON
# =========================================================
#
# This creates the Telegram top-side:
#
# ☰ Menu
#     🌐 Open / Wake Bot
#
# Clicking it opens your Render URL inside Telegram.
# =========================================================

async def setup_bot_menu(application: Application):
    try:
        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="🌐 Open / Wake Bot",
                web_app=WebAppInfo(url=RENDER_URL),
            )
        )

        print("✅ Telegram Menu Button configured successfully.")

    except Exception as e:
        print(f"⚠️ Failed to configure Telegram Menu Button: {e}")


# =========================================================
# HEALTH SERVER FOR RENDER
# =========================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Birthday Calculator Bot</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
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
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
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
        <h1>🎂 Birthday Calculator Bot</h1>
        <p>🟢 Bot service is running.</p>
        <p>You can return to Telegram and use the bot.</p>
    </div>
</body>
</html>
"""

        body = html.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)

    print(f"🌐 Health server running on port {PORT}")

    server.serve_forever()


# =========================================================
# /START
# =========================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Clear previous birthday calculation data
    context.user_data.clear()

    user = update.effective_user

    first_name = user.first_name or "there"

    text = (
        f"🎉 Hello {first_name}!\n\n"
        "🎂 Welcome to Birthday Calculator Bot!\n\n"
        "You can calculate your age, next birthday, "
        "zodiac signs, life statistics, milestones, "
        "birthday card and many more things.\n\n"
        "👇 Choose an option from the menu below."
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_MARKUP
    )


# =========================================================
# HELP
# =========================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = (
        "📖 Birthday Calculator Bot Help\n\n"
        "🏠 /start — Open the main menu\n"
        "🎂 Birthday Calculator — Calculate your birthday information\n"
        "❌ /cancel — Cancel current calculation\n"
        "📖 /help — Show this help\n\n"
        "🌐 You can also use the Telegram ☰ Menu "
        "to open the Render service."
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_MARKUP
    )


# =========================================================
# CANCEL
# =========================================================

async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Current calculation cancelled.\n\n"
        "🏠 You are back at the main menu.",
        reply_markup=MAIN_MARKUP
    )


# =========================================================
# DEVELOPER
# =========================================================

async def developer_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    developer_text = (
        "👨‍💻 Developer\n\n"
        "Name: MASTERMIND\n"
        f"Telegram: {DEVELOPER_USERNAME}\n"
    )

    if DEVELOPER_ID:
        developer_text += f"Telegram ID: {DEVELOPER_ID}\n"
    else:
        developer_text += "Telegram ID: Not provided\n"

    developer_text += (
        "\n🎂 Birthday Calculator Bot"
        "\n🌐 Render service is available from the Telegram ☰ Menu."
    )

    await update.message.reply_text(
        developer_text,
        reply_markup=MAIN_MARKUP
    )


# =========================================================
# RENDER LINK BUTTON
# =========================================================

async def render_link_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🌐 Open / Wake Bot",
                url=RENDER_URL
            )
        ]
    ])

    await update.message.reply_text(
        "🌐 Open the Render service:",
        reply_markup=keyboard
    )


# =========================================================
# TEXT ROUTER
# =========================================================

async def text_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # Main menu
    if text == START_BUTTON:
        await start_command(update, context)
        return

    # Birthday Calculator
    if text == BIRTHDAY_BUTTON:
        await birthday_start(update, context)
        return

    # Developer
    if text == DEVELOPER_BUTTON:
        await developer_command(update, context)
        return

    # Otherwise send message to birthday calculator handler
    await birthday_handler(update, context)


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    print(
        "⚠️ Exception while handling update:",
        context.error
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print("🚀 Starting Birthday Calculator Bot...")

    # Start Render health server in background
    health_thread = Thread(
        target=start_health_server,
        daemon=True
    )

    health_thread.start()

    # Build Telegram application
    application = (
        Application.builder()
        .token(TOKEN)
        .post_init(setup_bot_menu)
        .build()
    )

    # -----------------------------------------------------
    # COMMAND HANDLERS
    # -----------------------------------------------------

    application.add_handler(
        CommandHandler("start", start_command)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        CommandHandler("cancel", cancel_command)
    )

    # Optional command for directly showing Render link
    application.add_handler(
        CommandHandler("render", render_link_command)
    )

    # -----------------------------------------------------
    # MESSAGE ROUTER
    # -----------------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_router
        )
    )

    # -----------------------------------------------------
    # ERROR HANDLER
    # -----------------------------------------------------

    application.add_error_handler(error_handler)

    print("🤖 Birthday Calculator Bot is running...")
    print("☰ Telegram Menu Button: 🌐 Open / Wake Bot")
    print(f"🌐 Render URL: {RENDER_URL}")

    # Start polling
    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()

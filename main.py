import os
import threading
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


# ============================================================
# CONFIG
# ============================================================

TOKEN = os.getenv("BOT_TOKEN")

RENDER_URL = os.getenv(
    "RENDER_URL",
    "https://cracker-birthday-calculator.onrender.com"
)

DEVELOPER_NAME = "MASTERMIND"
DEVELOPER_USERNAME = "@Do*x*Die"

DEVELOPER_ID = os.getenv(
    "DEVELOPER_ID",
    ""
)


if not TOKEN:
    raise ValueError(
        "BOT_TOKEN environment variable is missing!"
    )


# ============================================================
# MAIN MENU
# ============================================================

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


# ============================================================
# START MESSAGE
# ============================================================

START_MESSAGE = """
╔════════════════════════════════════╗
║       ⚡ CALCULATOR UNIVERSE ⚡      ║
╚════════════════════════════════════╝

Welcome to Calculator Universe.

A collection of useful calculators
inside one powerful Telegram bot.

🎂 Birthday Calculator
📆 Date Difference Calculator
👨‍💻 Developer Information

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select an option from the menu below.
"""


# ============================================================
# DEVELOPER
# ============================================================

async def developer_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    developer_id = (
        str(DEVELOPER_ID)
        if DEVELOPER_ID
        else "Not provided"
    )

    message = f"""
╔════════════════════════════════════╗
║          👨‍💻 DEVELOPER             ║
╚════════════════════════════════════╝

⚡ Name:
{DEVELOPER_NAME}

📱 Telegram:
{DEVELOPER_USERNAME}

🆔 Developer ID:
{developer_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Calculator Universe

Built with:
• Python
• Telegram Bot API
• Render

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❤️ Thanks for using the bot.
"""

    await update.message.reply_text(
        message,
        reply_markup=MAIN_MARKUP
    )


# ============================================================
# START COMMAND
# ============================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    await update.message.reply_text(
        START_MESSAGE,
        reply_markup=MAIN_MARKUP
    )


# ============================================================
# HELP COMMAND
# ============================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = """
╔════════════════════════════════════╗
║              🆘 HELP              ║
╚════════════════════════════════════╝

🎂 Birthday Calculator

Calculate:

• Current age
• Next birthday
• Birthday countdown
• Zodiac information
• Life statistics
• Age milestones
• Birthday card


📆 Date Difference Calculator

Enter two dates.

Example:

23/9/26
29/9/26

Or:

23/09/2026
29/09/2026

The calculator can show:

• Total days
• Weeks + days
• Hours
• Minutes
• Seconds
• Calendar difference
• Weekdays
• Weekend information
• Leap-year information
• Day of year
• Countdown information

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏠 Use /start for the main menu.

❌ Use /cancel to cancel
the current calculation.
"""

    await update.message.reply_text(
        message,
        reply_markup=MAIN_MARKUP
    )


# ============================================================
# CANCEL
# ============================================================

async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Current calculation cancelled.",
        reply_markup=MAIN_MARKUP
    )


# ============================================================
# TEXT ROUTER
# ============================================================

async def text_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
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
    # BIRTHDAY
    # --------------------------------------------------------

    if text == BIRTHDAY_BUTTON:

        context.user_data.clear()

        await birthday_start(
            update,
            context
        )

        return


    # --------------------------------------------------------
    # DATE DIFFERENCE
    # --------------------------------------------------------

    if text == DATE_CALCULATOR_BUTTON:

        context.user_data.clear()

        await date_calculator_start(
            update,
            context
        )

        return


    # --------------------------------------------------------
    # DATE CALCULATOR ACTIVE
    # --------------------------------------------------------

    if is_date_calculator_active(context):

        await date_calculator_handler(
            update,
            context
        )

        return


    # --------------------------------------------------------
    # DEVELOPER
    # --------------------------------------------------------

    if text == DEVELOPER_BUTTON:

        await developer_handler(
            update,
            context
        )

        return


    # --------------------------------------------------------
    # BIRTHDAY INPUT / ROUTER
    # --------------------------------------------------------

    await birthday_message_handler(
        update,
        context
    )


# ============================================================
# BEAUTIFUL RENDER WEB PAGE
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        html = """
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width,
    initial-scale=1.0,
    maximum-scale=1.0,
    user-scalable=no"
>

<meta
    name="theme-color"
    content="#020307"
>

<title>MASTERMIND</title>


<style>

/* ============================================================
   RESET
============================================================ */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
}


/* ============================================================
   BODY
============================================================ */

html,
body {

    width: 100%;

    min-height: 100%;

}


body {

    min-height: 100vh;

    overflow: hidden;

    background: #020307;

    color: white;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

}


/* ============================================================
   BACKGROUND
============================================================ */

.background {

    position: fixed;

    inset: 0;

    overflow: hidden;

    background:

        radial-gradient(
            circle at 15% 20%,
            rgba(255,0,50,.20),
            transparent 30%
        ),

        radial-gradient(
            circle at 85% 25%,
            rgba(0,100,255,.20),
            transparent 32%
        ),

        radial-gradient(
            circle at 50% 100%,
            rgba(255,0,45,.12),
            transparent 35%
        ),

        #020307;

}


/* ============================================================
   RED LIGHT
============================================================ */

.redGlow {

    position: absolute;

    width: 380px;

    height: 380px;

    border-radius: 50%;

    background:
        rgba(255,0,50,.30);

    filter: blur(110px);

    left: -180px;

    top: 5%;

    animation:
        redMove
        7s
        ease-in-out
        infinite
        alternate;

}


@keyframes redMove {

    0% {

        transform:
            translate(0,0)
            scale(1);

    }

    100% {

        transform:
            translate(210px,120px)
            scale(1.35);

    }

}


/* ============================================================
   BLUE LIGHT
============================================================ */

.blueGlow {

    position: absolute;

    width: 380px;

    height: 380px;

    border-radius: 50%;

    background:
        rgba(0,90,255,.28);

    filter: blur(110px);

    right: -180px;

    top: 20%;

    animation:
        blueMove
        8s
        ease-in-out
        infinite
        alternate;

}


@keyframes blueMove {

    0% {

        transform:
            translate(0,0)
            scale(1);

    }

    100% {

        transform:
            translate(-200px,-120px)
            scale(1.3);

    }

}


/* ============================================================
   GRID
============================================================ */

.grid {

    position: absolute;

    inset: 0;

    opacity: .32;

    background-image:

        linear-gradient(
            rgba(255,255,255,.045) 1px,
            transparent 1px
        ),

        linear-gradient(
            90deg,
            rgba(255,255,255,.045) 1px,
            transparent 1px
        );

    background-size:
        45px 45px;

    transform:
        perspective(500px)
        rotateX(55deg)
        scale(1.7);

    transform-origin:
        center bottom;

    animation:
        gridMove
        8s
        linear
        infinite;

}


@keyframes gridMove {

    from {

        background-position:
            0 0;

    }

    to {

        background-position:
            0 90px;

    }

}


/* ============================================================
   PARTICLES
============================================================ */

#particles {

    position: absolute;

    inset: 0;

}


.particle {

    position: absolute;

    width: 3px;

    height: 3px;

    border-radius: 50%;

    background: white;

    box-shadow:
        0 0 10px
        rgba(255,255,255,.8);

    animation:
        particleMove
        linear
        infinite;

}


@keyframes particleMove {

    from {

        transform:
            translateY(110vh)
            translateX(0);

        opacity: 0;

    }

    15% {

        opacity: .8;

    }

    85% {

        opacity: .8;

    }

    to {

        transform:
            translateY(-20vh)
            translateX(80px);

        opacity: 0;

    }

}


/* ============================================================
   MAIN
============================================================ */

.main {

    position: relative;

    z-index: 10;

    width: 100%;

    min-height: 100vh;

    display: flex;

    align-items: center;

    justify-content: center;

    padding: 20px;

}


/* ============================================================
   GLASS PANEL
============================================================ */

.panel {

    position: relative;

    width:
        min(900px,100%);

    padding:
        55px 35px 30px;

    border-radius:
        35px;

    background:
        rgba(5,7,14,.72);

    border:
        1px solid
        rgba(255,255,255,.11);

    backdrop-filter:
        blur(25px);

    -webkit-backdrop-filter:
        blur(25px);

    box-shadow:

        0 0 80px
        rgba(0,0,0,.8),

        0 0 120px
        rgba(255,0,50,.08),

        inset
        0 0 60px
        rgba(255,255,255,.025);

    animation:
        panelIn
        1.4s
        cubic-bezier(.16,1,.3,1);

}


@keyframes panelIn {

    from {

        opacity: 0;

        transform:
            translateY(80px)
            scale(.88)
            rotateX(12deg);

    }

    to {

        opacity: 1;

        transform:
            translateY(0)
            scale(1)
            rotateX(0);

    }

}


/* ============================================================
   TOP ENERGY LINE
============================================================ */

.topLine {

    position: absolute;

    top: 0;

    left: 10%;

    width: 80%;

    height: 2px;

    background:

        linear-gradient(
            90deg,
            transparent,
            #ff174d,
            #287cff,
            transparent
        );

    box-shadow:

        0 0 20px #ff174d,

        0 0 30px #287cff;

    animation:
        linePulse
        2s
        ease-in-out
        infinite;

}


@keyframes linePulse {

    0%,100% {

        opacity: .5;

        transform:
            scaleX(.7);

    }

    50% {

        opacity: 1;

        transform:
            scaleX(1);

    }

}


/* ============================================================
   STATUS
============================================================ */

.status {

    display: flex;

    justify-content: center;

    margin-bottom: 30px;

}


.statusBox {

    display: flex;

    align-items: center;

    gap: 9px;

    padding:
        8px 14px;

    border-radius: 50px;

    background:
        rgba(255,255,255,.04);

    border:
        1px solid
        rgba(255,255,255,.09);

    color:
        rgba(255,255,255,.65);

    font-size: 10px;

    font-weight: bold;

    letter-spacing: 3px;

}


.dot {

    width: 7px;

    height: 7px;

    border-radius: 50%;

    background:
        #ff174d;

    box-shadow:

        0 0 7px #ff174d,

        0 0 20px #ff174d;

    animation:
        dotPulse
        1.2s
        infinite;

}


@keyframes dotPulse {

    50% {

        transform:
            scale(1.7);

        opacity: .5;

    }

}


/* ============================================================
   ORB
============================================================ */

.orb {

    position: relative;

    width: 115px;

    height: 115px;

    margin:
        0 auto 30px;

    border-radius: 50%;

    background:

        radial-gradient(
            circle at 30% 25%,
            white 0%,
            #7ba2ff 7%,
            #174dff 25%,
            #080e28 55%,
            #020307 72%
        );

    box-shadow:

        0 0 25px
        rgba(0,100,255,.7),

        0 0 70px
        rgba(0,80,255,.35),

        inset
        -15px -20px 30px
        rgba(0,0,0,.8);

    animation:
        orbFloat
        4s
        ease-in-out
        infinite;

}


.orb::before {

    content: "";

    position: absolute;

    inset: -16px;

    border-radius: 50%;

    border:
        1px solid
        rgba(0,110,255,.7);

    box-shadow:
        0 0 25px
        rgba(0,100,255,.4);

    animation:
        ringRotate
        5s
        linear
        infinite;

}


.orb::after {

    content: "";

    position: absolute;

    inset: -30px;

    border-radius: 50%;

    border:
        1px solid
        rgba(255,0,55,.45);

    box-shadow:
        0 0 20px
        rgba(255,0,55,.2);

    animation:
        ringRotate
        9s
        linear
        infinite reverse;

}


@keyframes orbFloat {

    0%,100% {

        transform:
            translateY(0)
            scale(1);

    }

    50% {

        transform:
            translateY(-12px)
            scale(1.04);

    }

}


@keyframes ringRotate {

    from {

        transform:
            rotate(0deg)
            scale(.95);

    }

    to {

        transform:
            rotate(360deg)
            scale(1.05);

    }

}


/* ============================================================
   MASTERMIND TITLE
============================================================ */

.title {

    text-align: center;

    font-size:
        clamp(40px,10vw,92px);

    line-height:
        .95;

    font-weight:
        1000;

    letter-spacing:
        clamp(3px,1vw,10px);

    color:
        white;

    text-shadow:

        0 0 5px white,

        0 0 15px
        rgba(255,0,50,.9),

        0 0 35px
        rgba(255,0,50,.65),

        0 0 70px
        rgba(0,100,255,.35);

    animation:
        titlePulse
        3s
        ease-in-out
        infinite;

}


@keyframes titlePulse {

    0%,100% {

        text-shadow:

            0 0 5px white,

            0 0 15px
            rgba(255,0,50,.8),

            0 0 35px
            rgba(255,0,50,.5);

    }

    50% {

        text-shadow:

            0 0 8px white,

            0 0 20px
            rgba(0,120,255,1),

            0 0 50px
            rgba(0,100,255,.8),

            0 0 90px
            rgba(255,0,50,.3);

    }

}


/* ============================================================
   SUBTITLE
============================================================ */

.subtitle {

    text-align: center;

    margin-top: 18px;

    color:
        rgba(255,255,255,.55);

    font-size:
        clamp(11px,2.5vw,16px);

    letter-spacing:
        6px;

    text-transform:
        uppercase;

}


/* ============================================================
   ENERGY
============================================================ */

.energy {

    width: 200px;

    height: 1px;

    margin:
        30px auto;

    background:

        linear-gradient(
            90deg,
            transparent,
            #ff174d,
            #287cff,
            transparent
        );

    box-shadow:
        0 0 15px
        rgba(255,0,50,.7);

    animation:
        energyPulse
        2s
        ease-in-out
        infinite;

}


@keyframes energyPulse {

    50% {

        width: 280px;

        opacity: .7;

    }

}


/* ============================================================
   FEATURES
============================================================ */

.features {

    display: grid;

    grid-template-columns:
        repeat(4,1fr);

    gap: 12px;

    margin-top: 25px;

}


.feature {

    position: relative;

    min-height: 120px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;

    border-radius: 20px;

    background:

        linear-gradient(
            145deg,
            rgba(255,255,255,.065),
            rgba(255,255,255,.018)
        );

    border:
        1px solid
        rgba(255,255,255,.08);

    overflow: hidden;

    transition:
        .35s ease;

}


.feature::before {

    content: "";

    position: absolute;

    width: 100%;

    height: 2px;

    top: 0;

    background:

        linear-gradient(
            90deg,
            transparent,
            rgba(255,0,55,.9),
            rgba(0,120,255,.9),
            transparent
        );

    transform:
        translateX(-100%);

    transition:
        .5s ease;

}


.feature:hover::before {

    transform:
        translateX(100%);

}


.feature:hover {

    transform:
        translateY(-8px)
        scale(1.02);

    background:
        rgba(255,255,255,.075);

    box-shadow:
        0 15px 35px
        rgba(0,0,0,.35);

}


.icon {

    font-size: 30px;

    margin-bottom: 10px;

    filter:
        drop-shadow(
            0 0 12px
            rgba(255,255,255,.35)
        );

}


.featureName {

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 1.5px;

    color:
        rgba(255,255,255,.9);

}


.featureDesc {

    margin-top: 6px;

    font-size: 8px;

    color:
        rgba(255,255,255,.35);

    letter-spacing: 1px;

}


/* ============================================================
   FOOTER
============================================================ */

.footer {

    display: flex;

    justify-content:
        space-between;

    margin-top: 28px;

    color:
        rgba(255,255,255,.28);

    font-size: 9px;

    letter-spacing: 2px;

}


.footer strong {

    color:
        rgba(255,255,255,.65);

}


/* ============================================================
   SCAN LINE
============================================================ */

.scan {

    position: absolute;

    left: 0;

    right: 0;

    height: 1px;

    background:

        linear-gradient(
            90deg,
            transparent,
            rgba(255,0,55,.6),
            rgba(0,110,255,.6),
            transparent
        );

    box-shadow:
        0 0 12px
        rgba(0,120,255,.7);

    animation:
        scanMove
        6s
        linear
        infinite;

}


@keyframes scanMove {

    from {

        top: 0;

        opacity: 0;

    }

    10% {

        opacity: 1;

    }

    90% {

        opacity: 1;

    }

    to {

        top: 100%;

        opacity: 0;

    }

}


/* ============================================================
   MOBILE
============================================================ */

@media (max-width: 700px) {

    body {

        overflow-y: auto;

    }


    .main {

        padding: 12px;

    }


    .panel {

        padding:
            38px 15px 22px;

        border-radius:
            27px;

    }


    .orb {

        width: 82px;

        height: 82px;

        margin-bottom: 24px;

    }


    .title {

        font-size:
            clamp(37px,12vw,60px);

        letter-spacing:
            3px;

    }


    .subtitle {

        font-size: 9px;

        letter-spacing: 3px;

    }


    .energy {

        width: 130px;

        margin:
            22px auto;

    }


    .features {

        grid-template-columns:
            repeat(2,1fr);

        gap: 9px;

        margin-top: 20px;

    }


    .feature {

        min-height: 95px;

        border-radius: 16px;

    }


    .icon {

        font-size: 23px;

        margin-bottom: 7px;

    }


    .featureName {

        font-size: 9px;

        letter-spacing: 1px;

    }


    .featureDesc {

        font-size: 7px;

    }


    .footer {

        flex-direction: column;

        align-items: center;

        gap: 8px;

        margin-top: 20px;

        text-align: center;

    }

}


/* ============================================================
   SMALL MOBILE
============================================================ */

@media (max-width: 360px) {

    .title {

        font-size: 34px;

    }


    .panel {

        padding-left: 11px;

        padding-right: 11px;

    }

}

</style>

</head>


<body>


<!-- ========================================================
     BACKGROUND
======================================================== -->

<div class="background">

    <div class="redGlow"></div>

    <div class="blueGlow"></div>

    <div class="grid"></div>

    <div id="particles"></div>

</div>


<!-- ========================================================
     MAIN
======================================================== -->

<div class="main">

    <div class="panel">

        <div class="topLine"></div>

        <div class="scan"></div>


        <!-- STATUS -->

        <div class="status">

            <div class="statusBox">

                <span class="dot"></span>

                SYSTEM ONLINE

            </div>

        </div>


        <!-- ORB -->

        <div class="orb"></div>


        <!-- TITLE -->

        <div class="title">
            MASTERMIND
        </div>


        <div class="subtitle">
            Calculator Universe
        </div>


        <div class="energy"></div>


        <!-- FEATURES -->

        <div class="features">


            <div class="feature">

                <div class="icon">
                    🎂
                </div>

                <div class="featureName">
                    BIRTHDAY
                </div>

                <div class="featureDesc">
                    AGE & COUNTDOWN
                </div>

            </div>


            <div class="feature">

                <div class="icon">
                    📆
                </div>

                <div class="featureName">
                    DATE DIFFERENCE
                </div>

                <div class="featureDesc">
                    DATE ANALYSIS
                </div>

            </div>


            <div class="feature">

                <div class="icon">
                    📊
                </div>

                <div class="featureName">
                    LIFE STATS
                </div>

                <div class="featureDesc">
                    DETAILED REPORT
                </div>

            </div>


            <div class="feature">

                <div class="icon">
                    🎯
                </div>

                <div class="featureName">
                    MILESTONES
                </div>

                <div class="featureDesc">
                    FUTURE DATES
                </div>

            </div>


        </div>


        <!-- FOOTER -->

        <div class="footer">

            <span>
                CALCULATOR UNIVERSE
            </span>

            <span>
                POWERED BY
                <strong>MASTERMIND</strong>
            </span>

        </div>


    </div>

</div>


<script>

/* ============================================================
   PARTICLES
============================================================ */

const particleContainer =
    document.getElementById("particles");


for (
    let i = 0;
    i < 70;
    i++
) {

    const particle =
        document.createElement("div");

    particle.className =
        "particle";

    particle.style.left =
        Math.random() * 100 + "%";

    particle.style.animationDuration =
        (
            5 +
            Math.random() * 12
        ) + "s";

    particle.style.animationDelay =
        (
            -Math.random() * 15
        ) + "s";

    const size =
        1 +
        Math.random() * 3;

    particle.style.width =
        size + "px";

    particle.style.height =
        size + "px";

    particleContainer.appendChild(
        particle
    );

}


/* ============================================================
   DESKTOP 3D EFFECT
============================================================ */

const panel =
    document.querySelector(".panel");


if (
    window.matchMedia(
        "(pointer:fine)"
    ).matches
) {

    document.addEventListener(
        "mousemove",
        function(event) {

            const x =
                (
                    event.clientX /
                    window.innerWidth
                ) - 0.5;

            const y =
                (
                    event.clientY /
                    window.innerHeight
                ) - 0.5;

            panel.style.transform =
                `
                perspective(1200px)
                rotateX(${y * -2}deg)
                rotateY(${x * 2}deg)
                `;

        }
    );


    document.addEventListener(
        "mouseleave",
        function() {

            panel.style.transform =
                "";

        }
    );

}

</script>


</body>

</html>
"""

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Cache-Control",
            "no-cache, no-store, must-revalidate"
        )

        self.send_header(
            "Pragma",
            "no-cache"
        )

        self.send_header(
            "Expires",
            "0"
        )

        self.end_headers()

        self.wfile.write(
            html.encode("utf-8")
        )


    def log_message(
        self,
        format,
        *args
    ):
        return


# ============================================================
# RENDER WEB SERVER
# ============================================================

def run_health_server():

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    print(
        f"🌐 Web server running on port {port}"
    )

    server.serve_forever()


# ============================================================
# TELEGRAM TOP MENU
# ============================================================

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

    print(
        "✅ Telegram Web App menu configured"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # START WEB SERVER
    # --------------------------------------------------------

    server_thread = threading.Thread(
        target=run_health_server,
        daemon=True
    )

    server_thread.start()


    # --------------------------------------------------------
    # TELEGRAM APPLICATION
    # --------------------------------------------------------

    application = (
        Application
        .builder()
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
    # TEXT
    # --------------------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_router
        )
    )


    # --------------------------------------------------------
    # LOG
    # --------------------------------------------------------

    print(
        "🚀 Calculator Universe Bot is running..."
    )

    print(
        f"👨‍💻 Developer: {DEVELOPER_NAME}"
    )

    print(
        f"📱 Telegram: {DEVELOPER_USERNAME}"
    )

    print(
        f"🌐 Web App: {RENDER_URL}"
    )


    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    application.run_polling(
        drop_pending_updates=True
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()

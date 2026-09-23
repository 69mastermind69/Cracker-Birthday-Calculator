from datetime import date, datetime, timedelta
from io import BytesIO
from zoneinfo import ZoneInfo
import calendar
import math
import os

from PIL import Image, ImageDraw, ImageFont

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InputFile,
)
from telegram.ext import ContextTypes


# =========================
# CONFIG
# =========================

BIRTHDAY_BUTTON = "🎂 Birthday Calculator"

TIMEZONE = os.getenv(
    "TIMEZONE",
    "Asia/Dhaka"
)


# =========================
# BUTTONS
# =========================

FULL_REPORT = "📋 Full Report"
NEXT_BIRTHDAY = "🎂 Next Birthday"
COUNTDOWN = "⏳ Countdown"

ZODIAC = "♈ Zodiac & Astrology"
LIFE_STATS = "📊 Life Statistics"
AGE_MILESTONES = "🎯 Age Milestones"

BIRTHDAY_CARD = "🖼 Birthday Card"

CALCULATE_AGAIN = "🔄 Calculate Again"
BACK = "⬅️ Back"


BIRTHDAY_KEYBOARD = [
    [FULL_REPORT],
    [NEXT_BIRTHDAY, COUNTDOWN],
    [ZODIAC],
    [LIFE_STATS],
    [AGE_MILESTONES],
    [BIRTHDAY_CARD],
    [CALCULATE_AGAIN],
    [BACK],
]

BIRTHDAY_MARKUP = ReplyKeyboardMarkup(
    BIRTHDAY_KEYBOARD,
    resize_keyboard=True
)


# =========================
# HELPERS
# =========================

def today_local():
    """
    Returns today's date using configured timezone.
    Default timezone: Asia/Dhaka
    """
    try:
        tz = ZoneInfo(TIMEZONE)
        return datetime.now(tz).date()
    except Exception:
        return date.today()


def parse_date(text: str):
    """
    Accepts:
    DD/MM/YYYY
    DD-MM-YYYY
    YYYY/MM/DD
    YYYY-MM-DD
    DD/MM/YY
    """

    text = text.strip()

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%d/%m/%y",
        "%d-%m-%y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return None


def safe_replace_year(d: date, year: int):
    """
    Handles February 29 when target year is not leap year.
    """
    try:
        return d.replace(year=year)
    except ValueError:
        return d.replace(
            year=year,
            month=2,
            day=28
        )


def calculate_age(birth_date: date, current_date: date):

    if current_date < birth_date:
        return 0, 0, 0

    years = current_date.year - birth_date.year

    birthday_this_year = safe_replace_year(
        birth_date,
        current_date.year
    )

    if current_date < birthday_this_year:
        years -= 1

    last_birthday = safe_replace_year(
        birth_date,
        birth_date.year + years
    )

    months = 0
    temp = last_birthday

    while True:
        next_month = temp.month + 1
        next_year = temp.year

        if next_month == 13:
            next_month = 1
            next_year += 1

        last_day = calendar.monthrange(
            next_year,
            next_month
        )[1]

        candidate = date(
            next_year,
            next_month,
            min(temp.day, last_day)
        )

        if candidate <= current_date:
            months += 1
            temp = candidate
        else:
            break

    days = (current_date - temp).days

    return years, months, days


def get_next_birthday(birth_date: date, current_date: date):

    target = safe_replace_year(
        birth_date,
        current_date.year
    )

    if target < current_date:
        target = safe_replace_year(
            birth_date,
            current_date.year + 1
        )

    return target


def calendar_difference(start: date, end: date):

    if end < start:
        return 0, 0, 0

    years = end.year - start.year

    candidate = safe_replace_year(
        start,
        start.year + years
    )

    if candidate > end:
        years -= 1
        candidate = safe_replace_year(
            start,
            start.year + years
        )

    months = 0

    while True:
        next_month = candidate.month + 1
        next_year = candidate.year

        if next_month == 13:
            next_month = 1
            next_year += 1

        last_day = calendar.monthrange(
            next_year,
            next_month
        )[1]

        next_date = date(
            next_year,
            next_month,
            min(candidate.day, last_day)
        )

        if next_date <= end:
            months += 1
            candidate = next_date
        else:
            break

    days = (end - candidate).days

    return years, months, days


# =========================
# WESTERN ZODIAC
# =========================

def western_zodiac(month, day):

    signs = [
        ("Capricorn", 1, 1, 1, 19),
        ("Aquarius", 1, 20, 2, 18),
        ("Pisces", 2, 19, 3, 20),
        ("Aries", 3, 21, 4, 19),
        ("Taurus", 4, 20, 5, 20),
        ("Gemini", 5, 21, 6, 20),
        ("Cancer", 6, 21, 7, 22),
        ("Leo", 7, 23, 8, 22),
        ("Virgo", 8, 23, 9, 22),
        ("Libra", 9, 23, 10, 22),
        ("Scorpio", 10, 23, 11, 21),
        ("Sagittarius", 11, 22, 12, 21),
        ("Capricorn", 12, 22, 12, 31),
    ]

    for sign, sm, sd, em, ed in signs:
        if (
            (month == sm and day >= sd)
            or
            (month == em and day <= ed)
        ):
            return sign

    return "Unknown"


# =========================
# CHINESE ZODIAC
# =========================

def chinese_zodiac(year):

    animals = [
        "Rat",
        "Ox",
        "Tiger",
        "Rabbit",
        "Dragon",
        "Snake",
        "Horse",
        "Goat",
        "Monkey",
        "Rooster",
        "Dog",
        "Pig",
    ]

    return animals[(year - 4) % 12]


# =========================
# LIFE PATH NUMBER
# =========================

def reduce_number(number):

    while number > 9 and number not in [11, 22, 33]:
        number = sum(
            int(x)
            for x in str(number)
        )

    return number


def life_path_number(birth_date):

    total = sum(
        int(x)
        for x in birth_date.strftime("%d%m%Y")
    )

    return reduce_number(total)


# =========================
# MOON PHASE
# =========================

def moon_phase(birth_date):

    # Approximate reference new moon
    reference = datetime(
        2000,
        1,
        6,
        18,
        14
    )

    target = datetime.combine(
        birth_date,
        datetime.min.time()
    )

    days = (
        target - reference
    ).total_seconds() / 86400

    synodic_month = 29.530588853

    phase_age = (
        days % synodic_month
    )

    fraction = (
        phase_age / synodic_month
    )

    if fraction < 0.03:
        name = "New Moon"
    elif fraction < 0.22:
        name = "Waxing Crescent"
    elif fraction < 0.28:
        name = "First Quarter"
    elif fraction < 0.47:
        name = "Waxing Gibbous"
    elif fraction < 0.53:
        name = "Full Moon"
    elif fraction < 0.72:
        name = "Waning Gibbous"
    elif fraction < 0.78:
        name = "Last Quarter"
    else:
        name = "Waning Crescent"

    return name, phase_age


# =========================
# LEAP YEARS
# =========================

def count_leap_days(birth_date, current_date):

    count = 0

    for year in range(
        birth_date.year,
        current_date.year + 1
    ):
        if calendar.isleap(year):
            try:
                leap_day = date(
                    year,
                    2,
                    29
                )

                if (
                    birth_date <= leap_day
                    <= current_date
                ):
                    count += 1

            except ValueError:
                pass

    return count


# =========================
# LIFE STATISTICS
# =========================

def life_statistics(
    birth_date,
    current_date
):

    total_days = (
        current_date - birth_date
    ).days

    total_hours = total_days * 24
    total_minutes = total_hours * 60
    total_seconds = total_minutes * 60

    # Approximate assumptions
    estimated_heartbeats = int(
        total_minutes * 70
    )

    estimated_sleep_hours = (
        total_days * 8
    )

    earth_revolutions = total_days

    leap_days = count_leap_days(
        birth_date,
        current_date
    )

    return {
        "days": total_days,
        "hours": total_hours,
        "minutes": total_minutes,
        "seconds": total_seconds,
        "heartbeats": estimated_heartbeats,
        "sleep_hours": estimated_sleep_hours,
        "earth_revolutions": earth_revolutions,
        "leap_days": leap_days,
    }


# =========================
# AGE MILESTONES
# =========================

def age_milestones(
    birth_date,
    current_date
):

    ages = [
        18,
        21,
        25,
        30,
        40,
        50,
        60,
        75,
        100,
    ]

    result = []

    for age in ages:

        milestone = safe_replace_year(
            birth_date,
            birth_date.year + age
        )

        if milestone < current_date:
            status = "Passed"
        elif milestone == current_date:
            status = "Today 🎉"
        else:
            days_left = (
                milestone - current_date
            ).days
            status = f"{days_left:,} days left"

        result.append(
            (
                age,
                milestone,
                status
            )
        )

    return result


def day_milestones(
    birth_date,
    current_date
):

    milestones = [
        1000,
        5000,
        10000,
        15000,
        20000,
        25000,
        30000,
    ]

    result = []

    for days in milestones:

        milestone_date = (
            birth_date
            + timedelta(days=days)
        )

        if milestone_date < current_date:
            status = "Passed"
        elif milestone_date == current_date:
            status = "Today 🎉"
        else:
            remaining = (
                milestone_date - current_date
            ).days
            status = f"{remaining:,} days left"

        result.append(
            (
                days,
                milestone_date,
                status
            )
        )

    return result


# =========================
# FULL DATA
# =========================

def calculate_all(birth_date):

    today = today_local()

    age_y, age_m, age_d = calculate_age(
        birth_date,
        today
    )

    next_bday = get_next_birthday(
        birth_date,
        today
    )

    countdown_days = (
        next_bday - today
    ).days

    countdown_y, countdown_m, countdown_d = (
        calendar_difference(
            today,
            next_bday
        )
    )

    western = western_zodiac(
        birth_date.month,
        birth_date.day
    )

    chinese = chinese_zodiac(
        birth_date.year
    )

    life_path = life_path_number(
        birth_date
    )

    moon, moon_age = moon_phase(
        birth_date
    )

    stats = life_statistics(
        birth_date,
        today
    )

    return {
        "today": today,
        "age_y": age_y,
        "age_m": age_m,
        "age_d": age_d,
        "next_birthday": next_bday,
        "next_birthday_weekday":
            next_bday.strftime("%A"),
        "countdown_days":
            countdown_days,
        "countdown_y":
            countdown_y,
        "countdown_m":
            countdown_m,
        "countdown_d":
            countdown_d,
        "turning_age":
            next_bday.year - birth_date.year,
        "born_weekday":
            birth_date.strftime("%A"),
        "western":
            western,
        "chinese":
            chinese,
        "life_path":
            life_path,
        "moon":
            moon,
        "moon_age":
            moon_age,
        "stats":
            stats,
        "age_milestones":
            age_milestones(
                birth_date,
                today
            ),
        "day_milestones":
            day_milestones(
                birth_date,
                today
            ),
    }


# =========================
# REPORTS
# =========================

def full_report(birth_date, data):

    s = data["stats"]

    text = (
        "🎂 BIRTHDAY CALCULATOR REPORT\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        f"📅 Birth Date: "
        f"{birth_date.strftime('%d %B %Y')}\n"

        f"📆 Born On: "
        f"{data['born_weekday']}\n\n"

        "🎂 AGE\n"
        f"• {data['age_y']} years, "
        f"{data['age_m']} months, "
        f"{data['age_d']} days\n\n"

        "🎉 NEXT BIRTHDAY\n"
        f"• {data['next_birthday'].strftime('%d %B %Y')}\n"
        f"• {data['next_birthday_weekday']}\n"
        f"• Turning {data['turning_age']}\n\n"

        "⏳ COUNTDOWN\n"
        f"• {data['countdown_days']:,} days\n"
        f"• Approx. {data['countdown_y']} years, "
        f"{data['countdown_m']} months, "
        f"{data['countdown_d']} days\n\n"

        "♈ ASTROLOGY\n"
        f"• Western Zodiac: {data['western']}\n"
        f"• Chinese Zodiac: {data['chinese']}\n"
        f"• Life Path Number: {data['life_path']}\n"
        f"• Moon Phase: {data['moon']}\n\n"

        "📊 LIFE STATISTICS\n"
        f"• Days lived: {s['days']:,}\n"
        f"• Hours: {s['hours']:,}\n"
        f"• Minutes: {s['minutes']:,}\n"
        f"• Seconds: {s['seconds']:,}\n"
        f"• Estimated heartbeats: "
        f"{s['heartbeats']:,}\n"
        f"• Estimated sleep: "
        f"{s['sleep_hours']:,} hours\n"
        f"• Earth revolutions: "
        f"{s['earth_revolutions']:,}\n"
        f"• Leap days experienced: "
        f"{s['leap_days']}\n\n"

        "ℹ️ Notes:\n"
        "• Time-based statistics are approximate "
        "because birth time is not provided.\n"
        "• Life Path Number is based on numerology.\n"
        "• Chinese Zodiac can differ for birthdays "
        "near Lunar New Year.\n"
        "• Moon phase is an approximation."
    )

    return text


def next_birthday_report(data):

    return (
        "🎂 NEXT BIRTHDAY\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📅 Date: "
        f"{data['next_birthday'].strftime('%d %B %Y')}\n"
        f"📆 Weekday: "
        f"{data['next_birthday_weekday']}\n"
        f"🎉 You will turn: "
        f"{data['turning_age']}\n\n"
        f"⏳ Days remaining: "
        f"{data['countdown_days']:,}\n"
        f"⏳ Calendar countdown: "
        f"{data['countdown_y']} years, "
        f"{data['countdown_m']} months, "
        f"{data['countdown_d']} days"
    )


def countdown_report(data):

    return (
        "⏳ BIRTHDAY COUNTDOWN\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎂 Next Birthday: "
        f"{data['next_birthday'].strftime('%d %B %Y')}\n\n"
        f"📅 {data['countdown_days']:,} days remaining\n\n"
        f"🗓 {data['countdown_y']} years, "
        f"{data['countdown_m']} months, "
        f"{data['countdown_d']} days\n\n"
        f"🎉 You will turn "
        f"{data['turning_age']}!"
    )


def zodiac_report(data):

    return (
        "♈ ZODIAC & ASTROLOGY\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"♈ Western Zodiac: "
        f"{data['western']}\n\n"
        f"🐉 Chinese Zodiac: "
        f"{data['chinese']}\n\n"
        f"🔢 Life Path Number: "
        f"{data['life_path']}\n"
        "(Numerology-based)\n\n"
        f"🌙 Moon Phase on Birth Date:\n"
        f"{data['moon']}\n\n"
        f"📆 Born on: "
        f"{data['born_weekday']}"
    )


def life_stats_report(data):

    s = data["stats"]

    return (
        "📊 LIFE STATISTICS\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📅 Days lived: "
        f"{s['days']:,}\n\n"

        f"⏰ Hours: "
        f"{s['hours']:,}\n\n"

        f"⏱ Minutes: "
        f"{s['minutes']:,}\n\n"

        f"⏱ Seconds: "
        f"{s['seconds']:,}\n\n"

        f"❤️ Estimated heartbeats: "
        f"{s['heartbeats']:,}\n"
        "(Approx. 70 BPM assumption)\n\n"

        f"😴 Estimated sleep: "
        f"{s['sleep_hours']:,} hours\n"
        "(Approx. 8 hours/day assumption)\n\n"

        f"🌍 Earth revolutions: "
        f"{s['earth_revolutions']:,}\n\n"

        f"📅 Leap days experienced: "
        f"{s['leap_days']}\n\n"

        "ℹ️ These are estimates, not exact "
        "measurements."
    )


def milestones_report(data):

    text = (
        "🎯 AGE MILESTONES\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for age, milestone, status in data["age_milestones"]:

        text += (
            f"🎂 Age {age}: "
            f"{milestone.strftime('%d %B %Y')}\n"
            f"   {status}\n\n"
        )

    text += (
        "📅 DAY MILESTONES\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for days, milestone, status in data["day_milestones"]:

        text += (
            f"📍 {days:,} days:\n"
            f"   {milestone.strftime('%d %B %Y')}\n"
            f"   {status}\n\n"
        )

    return text


# =========================
# BIRTHDAY CARD
# =========================

def get_font(size):

    possible_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]

    for font_path in possible_fonts:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(
                    font_path,
                    size
                )
            except Exception:
                pass

    return ImageFont.load_default()


def create_birthday_card(
    birth_date,
    data
):

    width = 1200
    height = 700

    image = Image.new(
        "RGB",
        (width, height),
        (20, 25, 45)
    )

    draw = ImageDraw.Draw(image)

    title_font = get_font(64)
    big_font = get_font(46)
    normal_font = get_font(32)
    small_font = get_font(24)

    # Decorative circles
    circles = [
        (70, 70, 150),
        (1050, 80, 115),
        (100, 560, 90),
        (1060, 550, 140),
    ]

    for x, y, r in circles:
        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r
            ),
            outline=(255, 210, 100),
            width=4
        )

    # Title
    title = "HAPPY BIRTHDAY!"

    bbox = draw.textbbox(
        (0, 0),
        title,
        font=title_font
    )

    title_width = bbox[2] - bbox[0]

    draw.text(
        (
            (width - title_width) / 2,
            80
        ),
        title,
        font=title_font,
        fill=(255, 220, 120)
    )

    # Birth date
    date_text = birth_date.strftime(
        "%d %B %Y"
    )

    bbox = draw.textbbox(
        (0, 0),
        date_text,
        font=big_font
    )

    date_width = bbox[2] - bbox[0]

    draw.text(
        (
            (width - date_width) / 2,
            190
        ),
        date_text,
        font=big_font,
        fill=(240, 240, 250)
    )

    # Age
    age_text = (
        f"Age: {data['age_y']} years, "
        f"{data['age_m']} months, "
        f"{data['age_d']} days"
    )

    bbox = draw.textbbox(
        (0, 0),
        age_text,
        font=normal_font
    )

    age_width = bbox[2] - bbox[0]

    draw.text(
        (
            (width - age_width) / 2,
            285
        ),
        age_text,
        font=normal_font,
        fill=(210, 220, 240)
    )

    # Zodiac
    zodiac_text = (
        f"Zodiac: {data['western']}   |   "
        f"Chinese: {data['chinese']}"
    )

    bbox = draw.textbbox(
        (0, 0),
        zodiac_text,
        font=normal_font
    )

    zodiac_width = bbox[2] - bbox[0]

    draw.text(
        (
            (width - zodiac_width) / 2,
            350
        ),
        zodiac_text,
        font=normal_font,
        fill=(220, 220, 240)
    )

    # Footer
    footer = (
        "Birthday Calculator Bot"
    )

    bbox = draw.textbbox(
        (0, 0),
        footer,
        font=small_font
    )

    footer_width = bbox[2] - bbox[0]

    draw.text(
        (
            (width - footer_width) / 2,
            600
        ),
        footer,
        font=small_font,
        fill=(180, 190, 210)
    )

    output = BytesIO()

    image.save(
        output,
        format="PNG"
    )

    output.seek(0)

    return output


# =========================
# BIRTHDAY START
# =========================

async def birthday_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    context.user_data[
        "birthday_state"
    ] = "waiting_for_birth_date"

    await update.message.reply_text(
        "🎂 Birthday Calculator\n\n"
        "Please enter your birth date.\n\n"
        "Accepted formats:\n"
        "• DD/MM/YYYY\n"
        "• DD-MM-YYYY\n"
        "• YYYY/MM/DD\n"
        "• YYYY-MM-DD\n\n"
        "Example:\n"
        "15/08/2005\n\n"
        "Use /cancel to cancel.",
        reply_markup=BIRTHDAY_MARKUP
    )


# =========================
# MESSAGE HANDLER
# =========================

async def birthday_message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = update.message.text.strip()

    state = context.user_data.get(
        "birthday_state"
    )

    # -------------------------
    # Back
    # -------------------------

    if text == BACK:

        context.user_data.clear()

        from main import MAIN_MARKUP

        await update.message.reply_text(
            "🏠 Back to main menu.",
            reply_markup=MAIN_MARKUP
        )

        return

    # -------------------------
    # Calculate Again
    # -------------------------

    if text == CALCULATE_AGAIN:

        context.user_data.clear()

        context.user_data[
            "birthday_state"
        ] = "waiting_for_birth_date"

        await update.message.reply_text(
            "🔄 Let's calculate again!\n\n"
            "Enter your birth date:\n\n"
            "Example: 15/08/2005",
            reply_markup=BIRTHDAY_MARKUP
        )

        return

    # -------------------------
    # Date input
    # -------------------------

    if state == "waiting_for_birth_date":

        birth_date = parse_date(text)

        if not birth_date:

            await update.message.reply_text(
                "❌ Invalid date format.\n\n"
                "Please use:\n"
                "DD/MM/YYYY\n\n"
                "Example:\n"
                "15/08/2005"
            )

            return

        today = today_local()

        if birth_date > today:

            await update.message.reply_text(
                "❌ Birth date cannot be in the future.\n\n"
                "Please enter a valid birth date."
            )

            return

        # Basic sanity check
        if birth_date.year < 1900:

            await update.message.reply_text(
                "❌ Please enter a birth year "
                "from 1900 onward."
            )

            return

        context.user_data[
            "birth_date"
        ] = birth_date

        data = calculate_all(
            birth_date
        )

        context.user_data[
            "birthday_data"
        ] = data

        context.user_data[
            "birthday_state"
        ] = "calculated"

        await update.message.reply_text(
            full_report(
                birth_date,
                data
            ),
            reply_markup=BIRTHDAY_MARKUP
        )

        return

    # -------------------------
    # If no birthday calculated
    # -------------------------

    if state != "calculated":

        await update.message.reply_text(
            "🎂 Please select "
            "Birthday Calculator first."
        )

        return

    # -------------------------
    # Retrieve data
    # -------------------------

    birth_date = context.user_data.get(
        "birth_date"
    )

    data = context.user_data.get(
        "birthday_data"
    )

    if not birth_date or not data:

        await birthday_start(
            update,
            context
        )

        return

    # -------------------------
    # Full Report
    # -------------------------

    if text == FULL_REPORT:

        await update.message.reply_text(
            full_report(
                birth_date,
                data
            ),
            reply_markup=BIRTHDAY_MARKUP
        )

        return

    # -------------------------
    # Next Birthday
    # -------------------------

    if text == NEXT_BIRTHDAY:

        await update.message.reply_text(
            next_birthday_report(data),
            reply_markup=BIRTHDAY_MARKUP
        )

        return

    # -------------------------
    # Countdown
    # -------------------------

    if text == COUNTDOWN:

        await update.message.reply_text(
            countdown_report(data),
            reply_markup=BIRTHDAY_MARKUP
        )

        return

    # -------------------------
    # Zodiac
    # -------------------------

    if text == ZODIAC:

        await update.message.reply_text(
            zodiac_report(data),
            reply_markup=BIRTHDAY_MARKUP
        )

        return

    # -------------------------
    # Life Statistics
    # -------------------------

    if text == LIFE_STATS:

        await update.message.reply_text(
            life_stats_report(data),
            reply_markup=BIRTHDAY_MARKUP
        )

        return

    # -------------------------
    # Milestones
    # -------------------------

    if text == AGE_MILESTONES:

        await update.message.reply_text(
            milestones_report(data),
            reply_markup=BIRTHDAY_MARKUP
        )

        return

    # -------------------------
    # Birthday Card
    # -------------------------

    if text == BIRTHDAY_CARD:

        try:

            card = create_birthday_card(
                birth_date,
                data
            )

            await update.message.reply_photo(
                photo=InputFile(
                    card,
                    filename="birthday_card.png"
                ),
                caption=(
                    "🎂 Your Birthday Card\n\n"
                    f"🎉 Turning {data['turning_age']} "
                    "on your next birthday!"
                ),
                reply_markup=BIRTHDAY_MARKUP
            )

        except Exception as error:

            print(
                "Birthday card error:",
                error
            )

            await update.message.reply_text(
                "❌ Sorry, I couldn't generate "
                "the birthday card right now."
            )

        return

    # -------------------------
    # Unknown text
    # -------------------------

    await update.message.reply_text(
        "Please use the buttons below.",
        reply_markup=BIRTHDAY_MARKUP
    )

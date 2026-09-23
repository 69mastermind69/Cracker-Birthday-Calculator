from datetime import date, datetime, time
from zoneinfo import ZoneInfo
import calendar
import os

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes


# ============================================================
# SETTINGS
# ============================================================

TIMEZONE = os.getenv("TIMEZONE", "Asia/Dhaka")

DATE_CALCULATOR_BUTTON = "📆 Date Difference Calculator"

DATE_CALCULATE_AGAIN = "🔄 Calculate Again"
DATE_BACK = "⬅️ Back"

DATE_KEYBOARD = [
    [DATE_CALCULATE_AGAIN],
    [DATE_BACK],
]

DATE_MARKUP = ReplyKeyboardMarkup(
    DATE_KEYBOARD,
    resize_keyboard=True
)


# ============================================================
# TIME / DATE HELPERS
# ============================================================

def now_local():
    try:
        return datetime.now(ZoneInfo(TIMEZONE))
    except Exception:
        return datetime.now()


def today_local():
    return now_local().date()


# ============================================================
# DATE PARSER
# ============================================================

def parse_date(text: str):
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


# ============================================================
# FORMATTING
# ============================================================

def format_date(d: date):
    return d.strftime("%d %B %Y")


def weekday_name(d: date):
    return d.strftime("%A")


def is_weekend(d: date):
    return d.weekday() >= 5


def weekend_text(d: date):
    return "Yes 🌴" if is_weekend(d) else "No"


def ordinal(n: int):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {
            1: "st",
            2: "nd",
            3: "rd"
        }.get(n % 10, "th")

    return f"{n}{suffix}"


def format_number(n):
    return f"{n:,}"


# ============================================================
# LEAP YEAR
# ============================================================

def is_leap_year(year: int):
    return calendar.isleap(year)


def count_leap_days(start: date, end: date):
    """
    Counts February 29 dates between start and end.
    """

    if start > end:
        start, end = end, start

    count = 0

    for year in range(start.year, end.year + 1):
        if calendar.isleap(year):
            leap_day = date(year, 2, 29)

            if start <= leap_day <= end:
                count += 1

    return count


# ============================================================
# CALENDAR DIFFERENCE
# ============================================================

def calendar_difference(start: date, end: date):
    """
    Returns calendar difference as years, months, days.
    """

    if start > end:
        start, end = end, start

    years = end.year - start.year
    months = end.month - start.month
    days = end.day - start.day

    if days < 0:
        months -= 1

        previous_month = end.month - 1

        if previous_month == 0:
            previous_month = 12
            previous_year = end.year - 1
        else:
            previous_year = end.year

        days_in_previous_month = calendar.monthrange(
            previous_year,
            previous_month
        )[1]

        days += days_in_previous_month

    if months < 0:
        years -= 1
        months += 12

    return years, months, days


# ============================================================
# DURATION
# ============================================================

def duration_from_days(days: int):
    total_seconds = days * 24 * 60 * 60

    hours = total_seconds // 3600
    minutes = total_seconds // 60
    seconds = total_seconds

    return total_seconds, hours, minutes, seconds


def detailed_duration(total_seconds: int):
    if total_seconds < 0:
        total_seconds = abs(total_seconds)

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return days, hours, minutes, seconds


# ============================================================
# YEAR INFORMATION
# ============================================================

def days_in_year(year):
    return 366 if calendar.isleap(year) else 365


def day_of_year(d: date):
    return d.timetuple().tm_yday


def days_remaining_in_year(d: date):
    return days_in_year(d.year) - day_of_year(d)


# ============================================================
# MONTH INFORMATION
# ============================================================

def days_in_month(d: date):
    return calendar.monthrange(d.year, d.month)[1]


def month_name(d: date):
    return d.strftime("%B")


# ============================================================
# DATE RELATION
# ============================================================

def date_relation(target: date, today: date):
    if target > today:
        return "future"

    if target < today:
        return "past"

    return "today"


# ============================================================
# LIVE COUNTDOWN
# ============================================================

def countdown_to_date(target_date: date):
    """
    Countdown to the START of target date at 00:00 local time.
    """

    now = now_local()

    target_datetime = datetime.combine(
        target_date,
        time.min
    )

    try:
        target_datetime = target_datetime.replace(
            tzinfo=ZoneInfo(TIMEZONE)
        )
    except Exception:
        pass

    difference = target_datetime - now

    total_seconds = int(difference.total_seconds())

    if total_seconds <= 0:
        return None

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return days, hours, minutes, seconds


# ============================================================
# REPORT
# ============================================================

def create_date_report(first_date: date, second_date: date):

    today = today_local()

    # Direction
    signed_difference = (second_date - first_date).days
    absolute_difference = abs(signed_difference)

    # Calendar difference
    cal_years, cal_months, cal_days = calendar_difference(
        first_date,
        second_date
    )

    # Duration
    total_seconds, total_hours, total_minutes, total_seconds = (
        duration_from_days(absolute_difference)
    )

    weeks = absolute_difference // 7
    remaining_days = absolute_difference % 7

    inclusive_days = absolute_difference + 1

    # Leap days
    leap_days = count_leap_days(first_date, second_date)

    # Target relation to today
    relation = date_relation(second_date, today)

    # Countdown
    countdown = None

    if relation == "future":
        countdown = countdown_to_date(second_date)

    # ========================================================
    # HEADER
    # ========================================================

    lines = [
        "╔══════════════════════════════╗",
        "       📆 DATE REPORT",
        "╚══════════════════════════════╝",
        "",
        "1️⃣ FIRST DATE",
        f"📅 {format_date(first_date)}",
        f"📆 {weekday_name(first_date)}",
        f"🔢 {ordinal(day_of_year(first_date))} day of the year",
        f"🌴 Weekend: {weekend_text(first_date)}",
        f"🗓 Leap Year: {'Yes 🐸' if is_leap_year(first_date.year) else 'No'}",
        f"📅 Month: {month_name(first_date)}",
        f"📊 Days in Month: {days_in_month(first_date)}",
        "",
        "2️⃣ SECOND DATE",
        f"📅 {format_date(second_date)}",
        f"📆 {weekday_name(second_date)}",
        f"🔢 {ordinal(day_of_year(second_date))} day of the year",
        f"🌴 Weekend: {weekend_text(second_date)}",
        f"🗓 Leap Year: {'Yes 🐸' if is_leap_year(second_date.year) else 'No'}",
        f"📅 Month: {month_name(second_date)}",
        f"📊 Days in Month: {days_in_month(second_date)}",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "📏 DATE DIFFERENCE",
        "",
        f"📅 Total Days: {format_number(absolute_difference)}",
        f"🗓 Weeks: {format_number(weeks)} weeks {remaining_days} days",
        f"📊 Calendar Difference: {cal_years} years, {cal_months} months, {cal_days} days",
        "",
        f"⏰ Total Hours: {format_number(total_hours)}",
        f"⏱ Total Minutes: {format_number(total_minutes)}",
        f"⚡ Total Seconds: {format_number(total_seconds)}",
        "",
        f"📌 Inclusive Calendar Days: {format_number(inclusive_days)}",
        "",
    ]

    # ========================================================
    # ORDER
    # ========================================================

    if signed_difference > 0:
        lines.extend([
            "➡️ DATE ORDER",
            "",
            "First date comes before second date.",
            f"⏩ Second date is {format_number(absolute_difference)} days after first date.",
            "",
        ])

    elif signed_difference < 0:
        lines.extend([
            "⬅️ DATE ORDER",
            "",
            "Second date comes before first date.",
            f"⏪ Second date is {format_number(absolute_difference)} days before first date.",
            "",
        ])

    else:
        lines.extend([
            "🟰 SAME DATE",
            "",
            "Both dates are exactly the same.",
            "",
        ])

    # ========================================================
    # TODAY
    # ========================================================

    lines.extend([
        "📍 TODAY",
        "",
        f"📅 Today: {format_date(today)}",
        f"📆 Today is: {weekday_name(today)}",
        "",
        f"🎯 Target Date: {format_date(second_date)}",
        f"📆 Target Day: {weekday_name(second_date)}",
        "",
    ])

    if relation == "future":

        days_until = (second_date - today).days

        lines.extend([
            "⏳ COUNTDOWN",
            "",
            f"🚀 {format_number(days_until)} days remaining",
        ])

        if countdown:
            c_days, c_hours, c_minutes, c_seconds = countdown

            lines.extend([
                "",
                "⏱ Live Countdown to 00:00",
                "",
                f"📅 {c_days} Days",
                f"⏰ {c_hours} Hours",
                f"⏱ {c_minutes} Minutes",
                f"⚡ {c_seconds} Seconds",
            ])

        lines.append("")

    elif relation == "today":

        lines.extend([
            "🎯 TARGET STATUS",
            "",
            "🔥 The target date is TODAY!",
            "",
        ])

    else:

        days_passed = (today - second_date).days

        lines.extend([
            "⏪ TARGET STATUS",
            "",
            f"Target date passed {format_number(days_passed)} days ago.",
            "",
        ])

    # ========================================================
    # EXTRA INFORMATION
    # ========================================================

    lines.extend([
        "📊 EXTRA INFORMATION",
        "",
        f"🐸 Leap Days Between Dates: {leap_days}",
        f"📅 {format_date(first_date)} → Day {day_of_year(first_date)} of year",
        f"📅 {format_date(second_date)} → Day {day_of_year(second_date)} of year",
        "",
        f"📆 Days Left in {first_date.year}: {days_remaining_in_year(first_date)}",
        f"📆 Days Left in {second_date.year}: {days_remaining_in_year(second_date)}",
        "",
        f"🌎 First Year: {first_date.year}",
        f"🌎 Second Year: {second_date.year}",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "💡 NOTE",
        "",
        "Hours, minutes and seconds above are based on full calendar days.",
        "For the live countdown, the target time is assumed to be 00:00 local time.",
    ])

    return "\n".join(lines)


# ============================================================
# START DATE CALCULATOR
# ============================================================

async def date_calculator_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    context.user_data["date_calc_state"] = "waiting_first_date"

    await update.message.reply_text(
        "📆 DATE DIFFERENCE CALCULATOR\n\n"
        "Let's calculate the difference between two dates.\n\n"
        "1️⃣ Enter the FIRST date.\n\n"
        "Example:\n"
        "23/9/26\n\n"
        "You can also use:\n"
        "23/09/2026\n"
        "23-09-2026\n"
        "2026-09-23",
        reply_markup=DATE_MARKUP
    )


# ============================================================
# DATE CALCULATOR HANDLER
# ============================================================

async def date_calculator_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    state = context.user_data.get("date_calc_state")

    # ========================================================
    # BACK
    # ========================================================

    if text == DATE_BACK:

        context.user_data.clear()

        from main import MAIN_MARKUP

        await update.message.reply_text(
            "⬅️ Back to main menu.",
            reply_markup=MAIN_MARKUP
        )

        return

    # ========================================================
    # CALCULATE AGAIN
    # ========================================================

    if text == DATE_CALCULATE_AGAIN:

        context.user_data.clear()

        context.user_data["date_calc_state"] = "waiting_first_date"

        await update.message.reply_text(
            "🔄 Let's calculate again!\n\n"
            "Enter the FIRST date.\n\n"
            "Example: 23/9/26",
            reply_markup=DATE_MARKUP
        )

        return

    # ========================================================
    # FIRST DATE
    # ========================================================

    if state == "waiting_first_date":

        first_date = parse_date(text)

        if first_date is None:

            await update.message.reply_text(
                "❌ Invalid date format.\n\n"
                "Please enter a valid date like:\n"
                "23/9/26\n"
                "23/09/2026\n"
                "23-09-2026\n"
                "2026-09-23",
                reply_markup=DATE_MARKUP
            )

            return

        context.user_data["date_calc_first_date"] = first_date
        context.user_data["date_calc_state"] = "waiting_second_date"

        await update.message.reply_text(
            f"✅ First date saved:\n"
            f"📅 {format_date(first_date)}\n"
            f"📆 {weekday_name(first_date)}\n\n"
            "2️⃣ Now enter the SECOND date.\n\n"
            "Example:\n"
            "29/9/26",
            reply_markup=DATE_MARKUP
        )

        return

    # ========================================================
    # SECOND DATE
    # ========================================================

    if state == "waiting_second_date":

        second_date = parse_date(text)

        if second_date is None:

            await update.message.reply_text(
                "❌ Invalid date format.\n\n"
                "Please enter a valid second date.\n\n"
                "Example: 29/9/26",
                reply_markup=DATE_MARKUP
            )

            return

        first_date = context.user_data.get(
            "date_calc_first_date"
        )

        if not first_date:

            context.user_data.clear()

            await date_calculator_start(
                update,
                context
            )

            return

        context.user_data["date_calc_second_date"] = second_date
        context.user_data["date_calc_state"] = "calculated"

        report = create_date_report(
            first_date,
            second_date
        )

        await update.message.reply_text(
            report,
            reply_markup=DATE_MARKUP
        )

        return

    # ========================================================
    # CALCULATED STATE
    # ========================================================

    if state == "calculated":

        await update.message.reply_text(
            "📆 Calculation complete!\n\n"
            "Use the buttons below:\n"
            "🔄 Calculate Again\n"
            "⬅️ Back",
            reply_markup=DATE_MARKUP
        )

        return

    # ========================================================
    # FALLBACK
    # ========================================================

    await date_calculator_start(
        update,
        context
    )


# ============================================================
# STATE CHECK
# ============================================================

def is_date_calculator_active(context):
    return bool(
        context.user_data.get("date_calc_state")
    )

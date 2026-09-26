import os
import telebot
import time
import json
import requests
import csv
from io import StringIO
from datetime import datetime, date, timedelta

from telebot import apihelper

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = str(message.chat.id)
    username = message.from_user.username or "Unknown"
    bot.reply_to(
        message,
        f"привет! у меня все норм я работаю")

@bot.message_handler(commands=['consultations'])
def consultations_handler(message):
    result = get_next_consultation()

    date_str = result["date"].strftime("%d.%m")

    if result["students"]:
        students = "\n".join(
            f"• {student}"
            for student in result["students"]
        )
    else:
        students = "Никто не записался."
    text = (
        f"Консультации {date_str}\n"
        f"{result['module']} модуль, {result['week']} неделя\n\n"
        f"{students}"
    )
    bot.reply_to(message, text)

SPREADSHEET_ID = "1pFTeYFAHoLUXgOSDF4eA4ckmdhn62Y6MsnPlUX87r50"

def scrape_data_from_spreadsheet():
    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{SPREADSHEET_ID}/export?format=csv"
    )

    response = requests.get(url)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    reader = csv.reader(StringIO(text))
    rows = list(reader)
    print(rows)
    return rows

CONSULTATION_COLUMNS = {
    1: 2,  # вторник -> колонка C
    4: 3,  # пятница -> колонка D
}

SCHEDULE = {
    date(2026, 8, 31): (1, 1),
    date(2026, 9, 7): (1, 2),
    date(2026, 9, 14): (1, 3),
    date(2026, 9, 21): (1, 4),

    #неделя с 2026, 9, 28 - кт

    date(2026, 10, 5): (2, 1),
    date(2026, 10, 12): (2, 2),
    date(2026, 10, 19): (2, 3),
    date(2026, 10, 26): (2, 4),

    #неделя с 2026, 11, 2 - кт

    date(2026, 11, 9): (2, 1),
    date(2026, 11, 16): (2, 2),
    date(2026, 11, 23): (2, 3),
    date(2026, 11, 30): (2, 4)
}

def get_next_consultation():
    rows = scrape_data_from_spreadsheet()
    now = datetime.now()
    next_date = None

    for days_ahead in range(8):
        current_date = (now + timedelta(days=days_ahead)).date()

        if current_date.weekday() in CONSULTATION_COLUMNS:
            next_date = current_date
            break
    week_start = max(
        start_date
        for start_date in SCHEDULE
        if start_date <= next_date
    )

    module, week = SCHEDULE[week_start]

    # Какая колонка нужна:
    # вторник = C = 2
    # пятница = D = 3
    column = CONSULTATION_COLUMNS[next_date.weekday()]

    target_week = f"{week} неделя"
    target_module = f"{module} модуль"

    # Ищем начало нужной недели
    start_row = None

    for i, row in enumerate(rows):
        if (
            len(row) >= 2
            and row[1].strip() == target_week
            and (
                row[0].strip() == target_module
                or row[0].strip() == ""
            )
        ):
            start_row = i
            break

    if start_row is None:
        return {
            "date": next_date,
            "module": module,
            "week": week,
            "students": [],
        }

    students = []
    if len(rows[start_row]) > column:
        student = rows[start_row][column].strip()

        if student:
            students.append(student)

    for row in rows[start_row + 1:]:
        # следующая неделя
        if len(row) >= 2 and row[1].strip().endswith("неделя"):
            break
        # следующий модуль
        if len(row) >= 1 and row[0].strip().endswith("модуль"):
            break
        if len(row) > column:
            student = row[column].strip()
            if student:
                students.append(student)

    return {
        "date": next_date,
        "module": module,
        "week": week,
        "students": students,
    }


if __name__ == "__main__":
    bot.polling(none_stop=True)
import os
import telebot
import random
import time
import sqlite3
import schedule
import threading
import json

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import apihelper


API_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = str(message.chat.id)
    username = message.from_user.username or "Unknown"
    add_user(user_id, username)

    bot.reply_to(
        message,
        f"meowmeowmeow")
    send_daily_message(user_id)

# @bot.callback_query_handler(func=lambda call: call.data == "open_image")
# def handle_open_image(call):
#     user_id = str(call.message.chat.id)
#     current_day = get_current_day()

#     user_images = get_user(user_id)
#     if not user_images:
#         bot.send_message(user_id, f"Похоже, что мы еще не знакомы. Отправь команду /start.")
#         return
    
#     sent_images = eval(user_images)  # Retrieve sent images as a list
#     remaining_days = current_day - len(sent_images)

#     if current_day == 31:
#         chosen_image = 'pictures/31.png'
#         bot.send_photo(user_id, open(chosen_image, 'rb'))
#         anekdot = anekdotes.get('31.png', "Анекдот не найден :()")
#         bot.send_message(user_id, anekdot)
#         sent_images.append(chosen_image)
#         update_user_images(user_id, str(sent_images))
#         remaining_days = current_day - len(sent_images)
#         if user_id == '620069122':
#             bot.send_message(user_id, "Саня, специально для тебя: чтоб хуй стоял и деньги были. с нг любимка!!!")
#         if remaining_days > 0:
#             bot.send_message(user_id, "Ты открыл не все доступные картинки. Нажми на кнопку 'открыть' еще раз!")
        



if __name__ == "__main__":
    #threading.Thread(target=schedule_daily_messages, daemon=True).start()
    bot.polling(none_stop=True)
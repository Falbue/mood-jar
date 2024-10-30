from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import types
import telebot

import config
from modules.scripts import *
from modules.commands import *


bot = telebot.TeleBot(config.API)  # создание бота

# КЛАВИАТУРЫ
btn_happy = types.InlineKeyboardButton("😊", callback_data='mood:Счастье')
btn_sad = types.InlineKeyboardButton("😢", callback_data='mood:Грусть')
btn_profile = InlineKeyboardButton(text="Профиль", callback_data="profile")
keyboard_main = InlineKeyboardMarkup(row_width=2)
keyboard_main.add(btn_happy, btn_sad)
keyboard_main.add(btn_profile)



commands = [  # КОМАНДЫ
telebot.types.BotCommand("start", "Перезапуск"),
]


# КОМАНДЫ
@bot.message_handler(commands=['start'])  # обработка команды start
def start(message):
    menu_id = registration(message)
    bot.send_message(message.chat.id, text="Добавить настроение", reply_markup=keyboard_main)
    bot.delete_message(message.chat.id, message.id)
    if menu_id:
        bot.delete_message(message.chat.id, menu_id)



# ОБРАБОТКА ВЫЗОВОВ
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):  # работа с вызовами inline кнопок
    user = SQL_request("SELECT * FROM users WHERE id = ?", (int(call.message.chat.id),))
    print(call.data)

    if call.data == 'profile':
        text = profile(user)
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=text)



print(f"бот запущен...")
bot.polling(none_stop=True)
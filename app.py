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

btn_return_main = InlineKeyboardButton(text="< Назад", callback_data='return:main')
btn_skip = InlineKeyboardButton(text="Пропустить >", callback_data='skip')
keyboard_mood_settings = InlineKeyboardMarkup(row_width = 2)
keyboard_mood_settings.add(btn_return_main, btn_skip)

def send_message(message, mood, message_id):
    add_mood(message.chat.id, mood, message.text)
    bot.delete_message(message.chat.id, message.message_id)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message_id, text="Добавить настроение", reply_markup=keyboard_main)


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
    user_id = call.message.chat.id
    message_id = call.message.message_id
    user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
    print(call.data)

    if call.data == 'profile':
        text = profile(user)
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=text)



print(f"бот запущен...")
bot.polling(none_stop=True)
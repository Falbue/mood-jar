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

keyboard_profile = InlineKeyboardMarkup(row_width=2)
keyboard_profile.add(btn_return_main)

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
        # text = profile(user)
        # bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=text)
        date, time = now_time()
        text = get_only_mood(user_id, date)
        text = text.replace("Счастье", "😊")
        text = text.replace("Грусть", "😢")
        text = format_emojis(text)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard_profile)

    if (call.data).split(":")[0] == 'mood':
        mood = (call.data).split(":")[1]
        text = f"Вы выбрали: {mood}\n\nВведите причину такого настроения"
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard_mood_settings)
        bot.register_next_step_handler(call.message, send_message, mood, message_id)

    if call.data == 'skip':
        mood = (call.message.text).split(": ")[1].split("\n")[0]
        add_mood(user_id, mood, "")
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Добавить настроение", reply_markup=keyboard_main)


    if (call.data).split(":")[0] == 'return':
        bot.clear_step_handler_by_chat_id(chat_id=user_id)
        if (call.data).split(":")[1] == 'main':
             bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Добавить настроение", reply_markup=keyboard_main)



print(f"бот запущен...")
bot.polling(none_stop=True)
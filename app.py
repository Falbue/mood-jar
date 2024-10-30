from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import types
import telebot

import config
from modules.scripts import *
from modules.commands import *

VERSION = "1.0.1.1"


bot = telebot.TeleBot(config.API)  # создание бота

# КЛАВИАТУРЫ
btn_return_main = InlineKeyboardButton(text="< Назад", callback_data='return:main')
btn_skip = InlineKeyboardButton(text="Пропустить >", callback_data='skip')
keyboard_mood_settings = InlineKeyboardMarkup(row_width = 2)
keyboard_mood_settings.add(btn_return_main, btn_skip)

keyboard_profile = InlineKeyboardMarkup(row_width=2)
keyboard_profile.add(btn_return_main)



def send_message(message, mood, message_id):
    add_mood(message.chat.id, mood, message.text)
    bot.delete_message(message.chat.id, message.message_id)
    keyboard_main = create_keyboard_main(message.chat.id)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message_id, text="Добавить настроение", reply_markup=keyboard_main)


def create_keyboard_main(user_id):
    btn_happy = types.InlineKeyboardButton("😊", callback_data='mood:Счастье')
    btn_sad = types.InlineKeyboardButton("😢", callback_data='mood:Грусть')
    btn_profile = InlineKeyboardButton(text="Профиль", callback_data="profile")
    keyboard_main = InlineKeyboardMarkup(row_width=2)
    keyboard_main.add(btn_happy, btn_sad)
    user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
    if user[2] != None:
        frend = SQL_request("SELECT * FROM users WHERE id = ?", (int(user[2]),))
        frend_name = frend[4]
        if frend[4] == None: frend_name = 'Друг'
        btn_frend = InlineKeyboardButton(text=frend_name, callback_data='frend')
    else:
        btn_frend = InlineKeyboardButton(text="Пригласить друга", switch_inline_query="Приглашение")
    keyboard_main.add(btn_frend, btn_profile)
    return keyboard_main



commands = [  # КОМАНДЫ
telebot.types.BotCommand("start", "Перезапуск"),
]


# КОМАНДЫ
@bot.message_handler(commands=['start'])  # обработка команды start
def start(message):
    menu_id = registration(message)
    keyboard_main = create_keyboard_main(message.chat.id)
    text = "Добавить настроение"
    if message.chat.id == config.ADMIN:
        text = f"{VERSION}\n\n{text}"
    bot.send_message(message.chat.id, text, reply_markup=keyboard_main)
    bot.delete_message(message.chat.id, message.id)
    if menu_id:
        bot.delete_message(message.chat.id, menu_id)



@bot.inline_handler(lambda query: query.query == 'Приглашение' or not query.query)
def default_query(inline_query):
    user_id = inline_query.from_user.id
    user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
    
    # Если запрос пустой
    if not inline_query.query:
        date, time = now_time()
        text = get_only_mood(user[0], date)
        text = text.replace("Счастье", "😊")
        text = text.replace("Грусть", "😢")
        text = format_emojis(text)
        bot.answer_inline_query(
            inline_query.id, 
            [
                types.InlineQueryResultArticle(
                    id='my_mood', 
                    title='Моя банка',
                    thumbnail_url="https://falbue.github.io/classroom-code/icons/registr.png",
                    description='Отправить мою банку',
                    input_message_content=types.InputTextMessageContent(
                        message_text=text
                    ),
                )
            ]
        )
    # Если запрос равен "Приглашение"
    else:
        bot.answer_inline_query(
            inline_query.id, 
            [
                types.InlineQueryResultArticle(
                    id='invite', 
                    title='Приглашение',
                    thumbnail_url="https://falbue.github.io/classroom-code/icons/registr.png",
                    description='Отправить приглашение',
                    input_message_content=types.InputTextMessageContent(
                        message_text="Приглашение"
                    ),
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton(
                            text='Перейти', 
                            callback_data=f"invite:{user[0]}"
                        )
                    )
                )
            ]
        )




# ОБРАБОТКА ВЫЗОВОВ
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):  # работа с вызовами inline кнопок
    if (call.data).split(":")[0] == 'invite':
        user_id = call.from_user.id
        if str(user_id) != str((call.data).split(":")[1]):
            user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
            if user ==  None or user == "":
                date, time  = now_time()
                SQL_request("""INSERT INTO users (id, message, time_registration)VALUES (?, ?, ?)""", (user_id, 1, date)) 
            SQL_request("UPDATE users SET frend = ? WHERE id = ?", (user_id, (call.data).split(":")[1]))
            SQL_request("UPDATE users SET frend = ? WHERE id = ?", ((call.data).split(":")[1], user_id))
            bot.edit_message_text(chat_id=None, inline_message_id=call.inline_message_id, text="Приглашение принято!", reply_markup=None)
        else:
            pass
    else:
        user_id = call.message.chat.id
        message_id = call.message.message_id
        user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
        print(call.data)

    if call.data == 'profile':
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
        keyboard_main = create_keyboard_main(user_id)
        text = "Добавить настроение"
        if user_id == config.ADMIN:
            text = f"{VERSION}\n\n{text}"
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard_main)

    if call.data == 'frend':
        date, time = now_time()
        text = get_only_mood(user[2], date)
        text = text.replace("Счастье", "😊")
        text = text.replace("Грусть", "😢")
        text = format_emojis(text)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard_profile)


    if (call.data).split(":")[0] == 'return':
        bot.clear_step_handler_by_chat_id(chat_id=user_id)
        if (call.data).split(":")[1] == 'main':
            keyboard_main = create_keyboard_main(user_id)
            text = "Добавить настроение"
            if user_id == config.ADMIN:
                text = f"{VERSION}\n\n{text}"
            bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard_main)
        



print(f"бот запущен...")
bot.polling(none_stop=True)
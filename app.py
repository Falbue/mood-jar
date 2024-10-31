from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import types
import telebot

import config
from modules.scripts import *
from modules.commands import *

VERSION = "1.0.2.1"


bot = telebot.TeleBot(config.API)  # создание бота

# КЛАВИАТУРЫ
btn_return_settings = InlineKeyboardButton("< Назад", callback_data='settings')

btn_return_main = InlineKeyboardButton(text="< Назад", callback_data='return:main')
btn_skip = InlineKeyboardButton(text="Пропустить >", callback_data='skip')
keyboard_mood_settings = InlineKeyboardMarkup(row_width = 2)
keyboard_mood_settings.add(btn_return_main, btn_skip)

keyboard_profile = InlineKeyboardMarkup(row_width=2)
btn_settings = InlineKeyboardButton("Настроки", callback_data='settings')
keyboard_profile.add(btn_return_main, btn_settings)

keyboard_settings = InlineKeyboardMarkup(row_width=2)
btn_edit_mood = InlineKeyboardButton('Настроения', callback_data='edit:mood')
btn_edit_topics = InlineKeyboardButton("Топики", callback_data='edit:topics')
btn_edit_frends = InlineKeyboardButton("Друзья", callback_data='edit:frends')
btn_return_profile = InlineKeyboardButton("< Назад", callback_data='profile')
keyboard_settings.add(btn_edit_mood, btn_edit_frends)
keyboard_settings.add(btn_return_profile)



def send_message(message, mood, message_id):
    add_mood(message.chat.id, mood, message.text)
    bot.delete_message(message.chat.id, message.message_id)
    keyboard_main = create_keyboard_main(message.chat.id)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message_id, text="Добавить настроение", reply_markup=keyboard_main)

def get_mood(message, edit, smile, message_id):
    get_text = message.text
    result = edit_value(message.chat.id, edit, smile, get_text)
    bot.delete_message(message.chat.id, message.message_id)
    keyboard = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("< Назад", callback_data=f"edit:{edit}")
    keyboard.add(btn)
    find_list(edit, message.chat.id, message_id)

def find_list(find, user_id, message_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    result = SQL_request(f"SELECT {find} FROM users WHERE id = ?", (user_id,))
    result = result[0]
    if result != None:
        result = json.loads(result)
        data = {}
        for key, value in result.items():
            new_value = f"{key} {value}"
            data[new_value] = key
        buttons = create_buttons(data, f'rename_{find}')
        keyboard.add(*buttons)
    btn_add = InlineKeyboardButton("Добавить +", callback_data=f'add:{find}')
    keyboard.add(btn_return_settings, btn_add)
    bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Выберите пункт, что бы его изменить", reply_markup=keyboard)

def create_buttons(data, prefix):
    # print(data)
    buttons = []
    for text, callback in data.items():
        if not isinstance(text, str):
            text = str(text)
        if callback == "":
            callback = text
        button = types.InlineKeyboardButton(text, callback_data=f'{prefix}:{callback}')
        buttons.append(button)
    return buttons


def create_keyboard_main(user_id):
    user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
    mood = user[7]
    if mood == None:
        buttons = []
        btn_add_mood = InlineKeyboardButton("Добавить настроение +", callback_data='add:mood')
        buttons.append(btn_add_mood)
    else:
        mood_dict = json.loads(mood)
        buttons = create_buttons(mood_dict, "mood")
        

    btn_profile = InlineKeyboardButton(text="Профиль", callback_data="profile")
    keyboard_main = InlineKeyboardMarkup(row_width=3)
    keyboard_main.add(*buttons)
    user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
    if user[2] != None:
        btn_frend = InlineKeyboardButton(text="Друзья", callback_data='frends')
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
    print(f"Кнопку создает {user_id}")
    user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
    if not inline_query.query:
        date, time = now_time()
        text = get_only_mood(user[0], date)
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
            ],
            cache_time=0
        )
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
            ],
            cache_time=0
        )





# ОБРАБОТКА ВЫЗОВОВ
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):  # работа с вызовами inline кнопок
    if (call.data).split(":")[0] == 'invite':
        user_id = call.from_user.id
        my_id = call.data.split(":")[1]
        result = add_frends(my_id, user_id, call)
        if result == True:
            bot.edit_message_text(chat_id=None, inline_message_id=call.inline_message_id, text="Приглашение принято!", reply_markup=None)
        else:
            pass
    else:
        user_id = call.message.chat.id
        bot.clear_step_handler_by_chat_id(chat_id=user_id)
        message_id = call.message.message_id
        user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
        SQL_request("UPDATE users SET username = ? WHERE id = ?", (call.from_user.username, user_id))
        print(user_id, call.data)

    if call.data == 'profile':
        date, time = now_time()
        text = get_only_mood(user_id, date)
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
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard_profile)

    if call.data == 'settings':
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Выберите, что хотите настроить", reply_markup=keyboard_settings)

    if (call.data).split(":")[0] == 'edit':
        find = (call.data).split(":")[1]
        find_list(find, user_id, message_id)

    if (call.data).split("_")[0] == 'rename':
        edit = (call.data).split("_")[1]
        edit = (edit).split(":")[0]
        mood = (call.data).split(":")[1]
        
        text = f"Введите новое настроение для {mood}"
        keyboard = InlineKeyboardMarkup()
        btn = InlineKeyboardButton("< Назад", callback_data=f"edit:{edit}")
        btn_delete = InlineKeyboardButton("Удалить", callback_data=f'delete_{edit}:{mood}')
        keyboard.add(btn, btn_delete)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard, parse_mode="MarkdownV2")
        bot.register_next_step_handler(call.message, get_mood, edit, mood, message_id)

    if (call.data).split("_")[0] == 'delete':
        edit = (call.data).split("_")[1]
        edit = (edit).split(":")[0]
        value = (call.data).split(":")[1]
        delete_value(user_id, value)
        find_list(edit, user_id, message_id)

    if (call.data).split(":")[0] == "add":
        edit = (call.data).split(":")[1]
        def next_step(message, edit):
            add_value(message, edit)
            bot.delete_message(message.chat.id, message.message_id)
            find_list(edit, user_id, message_id)      
        bot.register_next_step_handler(call.message, next_step, edit)
        text = f"Введите смайлик, что бы добавить новое настроение"
        keyboard = InlineKeyboardMarkup()
        btn = InlineKeyboardButton("< Назад", callback_data=f"edit:{edit}")
        keyboard.add(btn)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard, parse_mode="MarkdownV2")

    if call.data == "frends":
        text = get_frends(user[2])
        print(text)





    if (call.data).split(":")[0] == 'return':
        if (call.data).split(":")[1] == 'main':
            keyboard_main = create_keyboard_main(user_id)
            text = "Добавить настроение"
            if user_id == config.ADMIN:
                text = f"{VERSION}\n\n{text}"
            bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard_main)
        



print(f"бот запущен...")
bot.polling(none_stop=True)
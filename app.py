from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import types
import telebot

import config
from modules.scripts import *
from modules.commands import *

VERSION = "1.4.1"


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
btn_edit_friends = InlineKeyboardButton("Друзья", callback_data='edit:friends')
btn_return_profile = InlineKeyboardButton("< Назад", callback_data='profile')
keyboard_settings.add(btn_edit_mood, btn_edit_friends)
keyboard_settings.add(btn_return_profile)

keyboard_friends = InlineKeyboardMarkup(row_width=2)
btn_return_friends_list = InlineKeyboardButton("< Назад", callback_data='friends')
keyboard_friends.add(btn_return_friends_list)



def send_message(message, mood, message_id):
    add_mood(message.chat.id, mood, message.text)
    bot.delete_message(message.chat.id, message.message_id)
    keyboard_main = create_keyboard_main(message.chat.id)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message_id, text="Добавить настроение", reply_markup=keyboard_main)

def get_value(message, edit, smile, message_id):
    get_text = message.text
    result = edit_value(message.chat.id, edit, smile, get_text)
    bot.delete_message(message.chat.id, message.message_id)
    keyboard = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("< Назад", callback_data=f"edit:{edit}")
    keyboard.add(btn)
    keyboard_edit(edit, message.chat.id, message_id)

def keyboard_edit(find, user_id, message_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    result = SQL_request(f"SELECT {find} FROM users WHERE id = ?", (user_id,))
    result = result[0]
    if result != None:
        result = json.loads(result)
        type_edit = "настроение"
        if find == "friends":
            type_edit = "друга"
            data = result
            btn_add = InlineKeyboardButton(text="Пригласить друга", switch_inline_query="Приглашение")
        else:
            btn_add = InlineKeyboardButton("Добавить +", callback_data=f'add:{find}')
            data = {}
            for key, value in result.items():
                new_value = f"{key} {value}"
                data[new_value] = key
        buttons = create_buttons(data, f'rename_{find}')
        keyboard.add(*buttons)
    keyboard.add(btn_return_settings, btn_add)
    bot.edit_message_text(chat_id=user_id, message_id=message_id, text=f"Выберите {type_edit}, что бы его изменить", reply_markup=keyboard)

def create_buttons(data, prefix):
    buttons = []
    for text, callback in data.items():
        if not isinstance(text, str):
            text = str(text)
        if callback == "":
            callback = text
        if prefix ==  "rename_friends" or prefix == "open_friends":
            button = types.InlineKeyboardButton(callback, callback_data=f'{prefix}:{text}')
        elif prefix ==  "mood":
            button = types.InlineKeyboardButton(text, callback_data=f'{prefix}:{text}')
        else:
            button = types.InlineKeyboardButton(text, callback_data=f'{prefix}:{callback}')
        buttons.append(button)
    return buttons


def create_keyboard_main(user_id):
    user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
    mood = user[7]
    if mood is None or mood == "{}" or mood == json.dumps({}):
        buttons = []
        btn_add_mood = InlineKeyboardButton("Добавить настроение +", callback_data='add:mood')
        buttons.append(btn_add_mood)
    else:
        mood_dict = json.loads(mood)
        buttons = create_buttons(mood_dict, "mood")
        

    btn_profile = InlineKeyboardButton(text="Профиль", callback_data="profile")
    keyboard_main = InlineKeyboardMarkup(row_width=3)
    keyboard_main.add(*buttons)
    if user[2] != "'{}'" or user[2] != None:
        btn_my_friends = InlineKeyboardButton(text="Друзья", callback_data='friends')
    else:
        btn_my_friends = InlineKeyboardButton(text="Пригласить друга", switch_inline_query="Приглашение")
    keyboard_main.add(btn_my_friends, btn_profile)
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
        result = add_friends(my_id, user_id, call)
        if result != False:
            bot.edit_message_text(chat_id=None, inline_message_id=call.inline_message_id, text=result, reply_markup=None)

    else:
        user_id = call.message.chat.id
        bot.clear_step_handler_by_chat_id(chat_id=user_id)
        message_id = call.message.message_id
        user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
        SQL_request("UPDATE users SET username = ? WHERE id = ?", (call.from_user.username, user_id))

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

    if call.data == "friends":
        text = user[2]
        text = json.loads(text)
        buttons = create_buttons(text, "open_friends")
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        keyboard.add(btn_return_main)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Ваши друзья", reply_markup=keyboard, parse_mode="MarkdownV2")

    if call.data == 'settings':
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Выберите, что хотите настроить", reply_markup=keyboard_settings)

    if (call.data).split(":")[0] == 'edit':
        find = (call.data).split(":")[1]
        keyboard_edit(find, user_id, message_id)

    if (call.data).split("_")[0] == 'rename':
        edit = (call.data).split("_")[1]
        edit = (edit).split(":")[0]
        find = (call.data).split(":")[1]
        
        text = f"Введите новое настроение для {find}"
        keyboard = InlineKeyboardMarkup()
        btn = InlineKeyboardButton("< Назад", callback_data=f"edit:{edit}")
        btn_delete = InlineKeyboardButton("Удалить", callback_data=f'delete_{edit}:{find}')
        keyboard.add(btn, btn_delete)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard)
        bot.register_next_step_handler(call.message, get_value, edit, find, message_id)

    if (call.data).split("_")[0] == 'delete':
        edit = (call.data).split("_")[1]
        edit = (edit).split(":")[0]
        value = (call.data).split(":")[1]
        delete_value(user_id, value, edit)
        keyboard_edit(edit, user_id, message_id)

    if (call.data).split(":")[0] == "add":
        edit = (call.data).split(":")[1]
        def next_step(message, edit):
            add_value(message, edit)
            bot.delete_message(message.chat.id, message.message_id)
            keyboard_edit(edit, user_id, message_id)      
        bot.register_next_step_handler(call.message, next_step, edit)
        text = f"Введите смайлик, что бы добавить новое настроение"
        keyboard = InlineKeyboardMarkup()
        btn = InlineKeyboardButton("< Назад", callback_data=f"edit:{edit}")
        keyboard.add(btn)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard, parse_mode="MarkdownV2")


    if (call.data).split(":")[0] == "open_friends":
        date, time = now_time()
        friend_id = int((call.data).split(":")[1])
        text = get_only_mood(friend_id, date)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard_friends)





    if (call.data).split(":")[0] == 'return':
        if (call.data).split(":")[1] == 'main':
            keyboard_main = create_keyboard_main(user_id)
            text = "Добавить настроение"
            if user_id == config.ADMIN:
                text = f"{VERSION}\n\n{text}"
            bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard_main)
        



print(f"бот запущен...")
bot.polling(none_stop=True)
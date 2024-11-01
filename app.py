from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import types
import telebot

import config
from modules.scripts import *
from modules.commands import *

VERSION = "1.6.0"


bot = telebot.TeleBot(config.API)  # создание бота

# КЛАВИАТУРЫ
btn_return_settings = InlineKeyboardButton("< Назад", callback_data='settings')
btn_settings = InlineKeyboardButton("⚙️Настройки⚙️", callback_data='settings')
btn_return_main = InlineKeyboardButton(text="< Назад", callback_data='return:main')

def send_message(message, mood, message_id, topic_list=None):   
    add_mood(message.chat.id, mood, message.text, topic_list)
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
    print(result)
    if result == None:
        result = "{}"
    result = json.loads(result)
    type_edit = "настроение"
    if find == "friends":
        type_edit = "друга"
        data = result
        btn_add = InlineKeyboardButton(text="Пригласить друга", switch_inline_query="Приглашение")
    if find == "topics":
        type_edit = "топик"
        data = result
        btn_add = InlineKeyboardButton("Добавить +", callback_data=f'add:{find}')
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
        if prefix ==  "rename_friends" or prefix == "profile" or prefix == 'rename_topics' or prefix == "topics" or prefix == "select_topics":
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
        

    btn_profile = InlineKeyboardButton(text="Профиль", callback_data=f"profile:{user[0]}")
    keyboard_main = InlineKeyboardMarkup(row_width=3)
    keyboard_main.add(*buttons)
    if user[2] == None or user[2] == json.dumps({}):
        btn_my_friends = InlineKeyboardButton(text="Пригласить друга", switch_inline_query="Приглашение")
    else:
        btn_my_friends = InlineKeyboardButton(text="Друзья", callback_data='friends')
    keyboard_main.add(btn_my_friends, btn_profile)
    return keyboard_main

def create_keyboard_mood_settings(user_id, select_topics=False):
    user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
    topics = user[5]
    if topics is None or topics == "{}" or topics == json.dumps({}):
        buttons = []
        btn_add_mood = InlineKeyboardButton("Добавить топик +", callback_data='add:topics')
        buttons.append(btn_add_mood)
    else:
        topics_dict = json.loads(topics)
        if select_topics:
            for key, value in topics_dict.items():
                if value in select_topics:
                    topics_dict[key] = "✅ " + value
        buttons = create_buttons(topics_dict, "select_topics")

    keyboard = InlineKeyboardMarkup(row_width = 3)
    btn_skip = InlineKeyboardButton(text="Пропустить >", callback_data='skip')
    keyboard.add(*buttons)
    keyboard.add(btn_return_main, btn_skip)
    return keyboard

def create_keyboard_profile(user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_info = InlineKeyboardButton("Информация", callback_data=f'info:{user_id}')
    btn_reasons = InlineKeyboardButton("Подробнее", callback_data=f'more_reasons:{user_id}')
    keyboard.add(btn_info, btn_reasons)
    return keyboard

def create_keyboard_settings(user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_edit_mood = InlineKeyboardButton('Настроения', callback_data='edit:mood')
    btn_edit_topics = InlineKeyboardButton("Топики", callback_data='edit:topics')
    btn_edit_friends = InlineKeyboardButton("Друзья", callback_data='edit:friends')
    btn_return_profile = InlineKeyboardButton("< Назад", callback_data=f'profile:{user_id}')
    keyboard.add(btn_edit_mood, btn_edit_friends, btn_edit_topics)
    keyboard.add(btn_return_profile)
    return keyboard

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
        text = get_mood_data(user[0], date)
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
        print(f"{user_id}: {call.data}")

    if (call.data).split(":")[0] == 'profile':
        date, time = now_time()
        text = get_mood_data((call.data).split(":")[1], date)
        keyboard = create_keyboard_profile((call.data).split(":")[1])
        if int((call.data).split(":")[1]) == int(user_id):
            keyboard.add(btn_settings)
            keyboard.add(btn_return_main)
        else:
            list_friends = InlineKeyboardButton(text="< Назад", callback_data='friends')
            keyboard.add(list_friends)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard)

    if (call.data).split(":")[0] == 'info':
        text = info_user((call.data).split(":")[1])
        if user_id == config.ADMIN:
            text = f"{VERSION}\n\n{text}"
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=text)

    if (call.data).split(":")[0] == 'mood':
        mood = (call.data).split(":")[1]
        text = f"Вы выбрали: {mood}\n\nВведите причину такого настроения"
        keyboard = create_keyboard_mood_settings(user_id)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard)
        bot.register_next_step_handler(call.message, send_message, mood, message_id)

    if call.data == 'skip':
        text = call.message.text
        if "Выбранные топики: " in text:
            existing_topics = text.split("Выбранные топики: ")[1]
            topic_list = existing_topics.split(", ")
        else: topic_list = None
        mood = (call.message.text).split(": ")[1].split("\n")[0]
        add_mood(user_id, mood, "", topic_list)
        keyboard_main = create_keyboard_main(user_id)
        text = "Добавить настроение"
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard_main)

    if (call.data).split(":")[0] == 'more_reasons':
        date, time = now_time()
        text = get_mood_data((call.data).split(":")[1], date, "text")
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text='< Назад', callback_data=f'profile:{(call.data).split(":")[1]}')))

    if call.data == "friends":
        text = user[2]
        text = json.loads(text)
        buttons = create_buttons(text, "profile")
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        keyboard.add(btn_return_main)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Ваши друзья", reply_markup=keyboard, parse_mode="MarkdownV2")

    if call.data == 'settings':
        keyboard = create_keyboard_settings(user_id)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Выберите, что хотите настроить", reply_markup=keyboard)

    if (call.data).split(":")[0] == 'edit':
        find = (call.data).split(":")[1]
        keyboard_edit(find, user_id, message_id)

    if (call.data).split("_")[0] == 'rename':
        edit = (call.data).split("_")[1]
        edit = (edit).split(":")[0]
        find = (call.data).split(":")[1]
        
        if edit == "mood":
            text = f"Введите новое настроение для {find}"
        elif edit == 'friends':
            text = f"Введите новое имя для друга"
        elif edit == "topics":
            text = f"Введите новое название топика"
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
            add_value(message, edit, edit)
            bot.delete_message(message.chat.id, message.message_id)
            keyboard_edit(edit, user_id, message_id)      
        bot.register_next_step_handler(call.message, next_step, edit)
        text = f"Введите смайлик, что бы добавить новое настроение"
        keyboard = InlineKeyboardMarkup()
        btn = InlineKeyboardButton("< Назад", callback_data=f"edit:{edit}")
        keyboard.add(btn)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard, parse_mode="MarkdownV2")

    if call.data.split(":")[0] == "select_topics":
        topic_dict = json.loads(user[5])
        bot.clear_step_handler_by_chat_id(chat_id=user_id)
        topic_id = call.data.split(":")[1]
        new_topic = topic_dict.get(topic_id, topic_id)  # Получаем значение из словаря или оставляем ID, если его нет
        text = call.message.text
        updated_topics = []
    
        # Проверка на наличие строки "Выбранные топики: " в тексте
        if "Выбранные топики: " not in text:
            text += f"\n\nВыбранные топики: {new_topic}"
            topic_list = [new_topic]
        else:
            # Извлекаем существующие топики и обрабатываем добавление/удаление
            existing_topics = text.split("Выбранные топики: ")[1]
            topic_list = existing_topics.split(", ")
    
            # Добавляем новый топик, если его нет; удаляем, если он уже есть
            if new_topic in topic_list:
                topic_list.remove(new_topic)
            else:
                topic_list.append(new_topic)
    
            # Обновляем текст с изменённым списком топиков
            text_topic = ", ".join(topic_list)
            text = text.split("Выбранные топики: ")[0] + f"Выбранные топики: {text_topic}"
    
        # Оставшийся код для изменения сообщения
        mood = text.split(": ")[1].split("\n")[0]
        keyboard = create_keyboard_mood_settings(user_id, topic_list)
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard)
        bot.register_next_step_handler(call.message, send_message, mood, message_id, topic_list)
    
    
    
    if (call.data).split(":")[0] == 'return':
        if (call.data).split(":")[1] == 'main':
            keyboard_main = create_keyboard_main(user_id)
            text = "Добавить настроение"
            bot.edit_message_text(chat_id=user_id, message_id=message_id, text=text, reply_markup=keyboard_main)
        
print(f"бот запущен...")
bot.polling(none_stop=True)
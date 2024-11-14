import json
from datetime import datetime
import pytz
import sqlite3
import os
import random

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))  # текущая директория скрипта
SCRIPT_DIR = os.path.dirname(PARENT_DIR)  # директория уровнем выше
DB_HUB = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), 'db_hub')
DB_HUB = SCRIPT_DIR if not (os.path.exists(DB_HUB) and os.path.isdir(DB_HUB)) else DB_HUB
DB_NAME = 'mood_jar.db'
DB_PATH = f"{DB_HUB}/{DB_NAME}"
VERSION = "1.9.1.3"

def now_time():  # Получение текущего времени по МСК
    now = datetime.now()
    tz = pytz.timezone('Europe/Moscow')
    now_moscow = now.astimezone(tz)
    current_time = now_moscow.strftime("%H:%M:%S")
    current_date = now_moscow.strftime("%Y.%m.%d")
    return current_date, current_time

def SQL_request(request, params=()):  # Выполнение SQL-запросов
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    if request.strip().lower().startswith('select'):
        cursor.execute(request, params)
        result = cursor.fetchone()
        connect.close()
        return result
    else:
        cursor.execute(request, params)
        connect.commit()
        connect.close()

def add_mood(user_id, mood, reason, topic_list):
    current_date, current_time = now_time()
    result = SQL_request("SELECT jar FROM users WHERE id = ?", (user_id,))
    if result and result[0]:
        mood_data = json.loads(result[0])
    else:
        mood_data = {}
    if current_date not in mood_data:
        mood_data[current_date] = {}

    mood_data[current_date][current_time] = {'mood': mood, 'reason': reason, "topics": topic_list}
    SQL_request("UPDATE users SET jar = ? WHERE id = ?", (json.dumps(mood_data, ensure_ascii=False), user_id)) 


def get_mood_data(user_id, date, mode="emojis"):
    result = SQL_request("SELECT jar FROM users WHERE id = ?", (user_id,))
    emoji_dict = SQL_request("SELECT mood FROM users WHERE id = ?", (user_id,))
    emoji_dict = json.loads(emoji_dict[0])
    if result and result[0]:
        mood_data = json.loads(result[0])
        if date in mood_data:
            if mode == "emojis":
                emojis = ''.join(entry["mood"] for time, entry in mood_data[date].items())
                return format_emojis(emojis)
            elif mode == "text":
                text = ''.join(
                    f'{entry["mood"]} ({emoji_dict.get(entry["mood"], "Неизвестно")})'
                    + (f' {", ".join(entry["topics"])}' if entry.get("topics") else "")
                    + f': {entry["reason"]}\n\n'
                    for time, entry in mood_data[date].items()
                )
                return text
        else:
            return "Сегодня пользователь ещё не добавил настроение"
    else:
        return "Пользователь ещё не пользовался банкой настроения"

def format_emojis(emojis, per_row=4, space="    "):
    grouped_emojis = [emojis[i:i + per_row] for i in range(0, len(emojis), per_row)]
    formatted_emojis = [space.join(group) for group in grouped_emojis]
    return '\n'.join(formatted_emojis)

def edit_value(user_id, edit, edit_value, text):
    text = text.replace(" ", "")
    result = SQL_request(f"SELECT {edit} FROM users WHERE id = ?", (user_id,))
    values = json.loads(result[0])
    values[edit_value] = text
    updated_values = json.dumps(values, ensure_ascii=False)
    SQL_request(f"UPDATE users SET {edit} = ? WHERE id = ?", (updated_values, user_id))
    return f"изменено!"

def delete_value(user_id, value, find):
    result = SQL_request(f"SELECT {find} FROM users WHERE id = ?", (user_id,))
    values = json.loads(result[0])
    if value in values:
        values.pop(value)
        delete_value = json.dumps(values, ensure_ascii=False)
        SQL_request(f"UPDATE users SET {find} = ? WHERE id = ?", (delete_value, user_id))
        return f"Запись с {value} удалена!"
    else:
        return f"Смайлик {smile} не найден в записях"

def add_value(message, edit, find):
    user_id = message.chat.id
    text = message.text

    result = SQL_request(f"SELECT {find} FROM users WHERE id = ?", (user_id,))
    if find == "mood" and (not isinstance(text, str) or len(text.split()) != 1):
        return {"notification": "Нужно отправить одно эмоджи!"}

    if result[0]:
        values = json.loads(result[0])
    else:
        values = {}
    if find == "topics":
        if values:
            new_id_topics = max(map(int, values.keys())) + 1
        else:
            new_id_topics = 1
        values[new_id_topics] = text
    else:
        values[text] = "ИЗМЕНИТЬ"
    updated_values = json.dumps(values, ensure_ascii=False)
    SQL_request(f"UPDATE users SET {find} = ? WHERE id = ?", (updated_values, user_id))
    if find == "mood": result = "Настроение добавлено!"
    if find == "topics": result = "Топик добавлен!"
    return {"notification": result}

def add_friends(my_id, frend_id, call):
    friend_name = call.from_user.first_name
    
    if str(my_id) != str(frend_id):
        user = SQL_request("SELECT * FROM users WHERE id = ?", (int(frend_id),))
        if user is None or user == "":
            date, time = now_time()
            mood = {"😊": "Радость", "😢": "Грусть", "😐": "Равнодушие", "😁": "Восторг", "😴": "Усталость"}
            topics = {"1": "Партнёр", "2": "Работа", "3": "Учёба", "4": "Здоровье", "5": "Друзья"}
            mood_json = json.dumps(mood, ensure_ascii=False)
            topics_json = json.dumps(topics, ensure_ascii=False)
            SQL_request("INSERT INTO users (id, message, mood, username, time_registration, topics) VALUES (?, ?, ?, ?, ?, ?)", (frend_id, 1, mood_json, friend_name, date, topics_json))
        
        user_friends = SQL_request("SELECT friends FROM users WHERE id = ?", (my_id,))
        friend_friends = SQL_request("SELECT friends FROM users WHERE id = ?", (frend_id,))
        
        user_friends = user_friends[0] if user_friends else None
        friend_friends = friend_friends[0] if friend_friends else None
        
        if user_friends is None:
            user_friends = {}
        else:
            user_friends = json.loads(user_friends)
        
        if friend_friends is None:
            friend_friends = {}
        else:
            friend_friends = json.loads(friend_friends)

        # if frend_id in user_friends:
        #     return "Вы уже добавлены в друзья"
        # if my_id in friend_friends:
        #     return "Этот пользователь уже добавил вас в друзья"
        
        user = SQL_request("SELECT * FROM users WHERE id = ?", (int(my_id),))
        user_friends[frend_id] = friend_name
        friend_friends[my_id] = user[4]
        
        SQL_request("UPDATE users SET friends = ? WHERE id = ?", (json.dumps(user_friends, ensure_ascii=False), my_id))
        SQL_request("UPDATE users SET friends = ? WHERE id = ?", (json.dumps(friend_friends, ensure_ascii=False), frend_id))
        
        return "Вы добавлены в друзья"
    else:
        return False

def get_friends(data):
    friends_list = {}
    friends = json.loads(data)
    for name, friend_id in friends.items():
        if name == "":
            friend_name = SQL_request("SELECT username FROM users WHERE id = ?", (int(friend_id),))
            friend_name = friend_name[0]
        else: friend_name = name
        friends_list[friend_name] = friend_id
    return friends_list

def info_user(user_id):
    user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
    if user[6] is not None:
        total_days = len(json.loads(user[6]))
        total_moods = sum(len(entries) for entries in json.loads(user[6]).values())
        stat = f"\nДней активности: {total_days}\nВсего настроений добавлено: {total_moods}\n"
    else: stat = ''
    if user[2] is not None: num_frends = len(json.loads(user[2]))
    else: num_frends = ""
    text = f"""Имя: {user[4]}
Всего друзей: {num_frends}
Дата регистрации: {user[3]}
{stat}
Версия: {VERSION} 
    """
    return text

def notif_friend(friend_id, type, user_id):  # уведомления для друзей
    user = SQL_request("SELECT * FROM users WHERE id = ?", (int(friend_id),))
    notif = user[9]
    notif = json.loads(notif) if notif is not None else {}
    if notif != None:
        notif[f"{user_id}"] = f"{type}"
    else: 
        notif = {f"{user_id}":f"{type}"}
    SQL_request("UPDATE users SET notif_friends = ? WHERE id = ?", (json.dumps(notif, ensure_ascii=False), friend_id))


def mood_message_friends(user_id, mood, text=None, topics=None):
    if topics is None:
        topic_text = ''
    else:
        topic_text = ' ' + ', '.join(topics)

    if text is None:
        text = ''

    notif_list = SQL_request("SELECT notif_friends FROM users WHERE id = ?", (int(user_id),))
    notif_list = json.loads(notif_list[0]) if notif_list[0] is not None else {}

    messages = []
    for user, notif_type in notif_list.items():
        if notif_type == 'add':
            friend_name = SQL_request("SELECT friends FROM users WHERE id = ?", (int(user),))
            friend_name = json.loads(friend_name[0])[str(user_id)]

            emoji_dict = SQL_request("SELECT mood FROM users WHERE id = ?", (user_id,))
            emoji_dict = json.loads(emoji_dict[0])

            message_text = f"{friend_name} добавил(а) новое настроение!\n\n{mood} ({emoji_dict.get(mood, '')}){topic_text}: {text}"
            messages.append((user, message_text))

    return messages

# ПРОВЕРКА СОЗДАНИЯ БД
if not os.path.exists(DB_PATH):
    SQL_request("""
        CREATE TABLE users (
            id INTEGER,
            message INTEGER, 
            friends JSON,
            time_registration TIME,
            username TEXT,
            topics TEXT,
            jar JSON,
            mood JSON,
            status TEXT,
            notif_friends TEXT
        )
    """)
    print("База данных создана")

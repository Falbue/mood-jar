import json
from datetime import datetime
import pytz
import sqlite3
import os

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))  # текущая директория скрипта
SCRIPT_DIR = os.path.dirname(PARENT_DIR)  # директория уровнем выше
DB_NAME = 'database.db'
DB_PATH = f"{SCRIPT_DIR}/{DB_NAME}"

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

def add_mood(user_id, mood, reason):
    current_date, current_time = now_time()
    result = SQL_request("SELECT jar FROM users WHERE id = ?", (user_id,))
    if result and result[0]:
        mood_data = json.loads(result[0])
    else:
        mood_data = {}
    if current_date not in mood_data:
        mood_data[current_date] = {}

    mood_data[current_date][current_time] = {'mood': mood, 'reason': reason}
    SQL_request("UPDATE users SET jar = ? WHERE id = ?", (json.dumps(mood_data, ensure_ascii=False), user_id))

def get_only_mood(user_id, date):
    result = SQL_request("SELECT jar FROM users WHERE id = ?", (user_id,))
    if result and result[0]:
        mood_data = json.loads(result[0])
        if date in mood_data:
            mood_message = ""
            emojis = ''.join(entry["mood"] for time, entry in mood_data[date].items())
            emojis = format_emojis(emojis)
            return emojis
        else:
            return "Нет записей настроений"
    else:
        return "Данные о настроении отсутствуют"

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
    print(f"Удаляем: {value}")
    result = SQL_request(f"SELECT {find} FROM users WHERE id = ?", (user_id,))
    values = json.loads(result[0])
    if value in values:
        values.pop(value)
        delete_value = json.dumps(values, ensure_ascii=False)
        SQL_request(f"UPDATE users SET {find} = ? WHERE id = ?", (delete_value, user_id))
        return f"Запись с {value} удалена!"
    else:
        return f"Смайлик {smile} не найден в записях"



def add_value(message, edit):
    user_id = message.chat.id
    smile = message.text
    result = SQL_request("SELECT mood FROM users WHERE id = ?", (user_id,))
    emotions = json.loads(result[0])
    emotions[smile] = ""
    updated_emotions = json.dumps(emotions, ensure_ascii=False)
    SQL_request("UPDATE users SET mood = ? WHERE id = ?", (updated_emotions, user_id))

def add_friends(my_id, frend_id, call):
    print(f"Кнопку создал {my_id}")
    print(f"Кнопку вызвал {frend_id}")
    friend_name = call.from_user.first_name
    
    if str(my_id) != str(frend_id):
        user = SQL_request("SELECT * FROM users WHERE id = ?", (int(frend_id),))
        if user is None or user == "":
            date, time = now_time()
            mood = {"😊": "Радость", "😢": "Грусть", "😐": "Равнодушие", "😁": "Восторг", "😴": "Усталость"}
            mood_json = json.dumps(mood, ensure_ascii=False)
            SQL_request("INSERT INTO users (id, message, mood, username, time_registration) VALUES (?, ?, ?, ?, ?)", (frend_id, 1, mood_json, friend_name, date))
        
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
        
        # Проверка на наличие одинаковых ключей
        if frend_id in user_friends:
            return "Вы уже добавлены в друзья"
        if my_id in friend_friends:
            return "Этот пользователь уже добавил вас в друзья"
        
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


# ПРОВЕРКА СОЗДАНИЯ БД
if not os.path.exists(DB_PATH):
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER,
            message INTEGER, 
            friends JSON,
            time_registration TIME,
            username TEXT,
            topics TEXT,
            jar JSON,
            mood JSON,
            status TEXT
        )
    """)
    connect.commit()
    connect.close()
    print("База данных создана")

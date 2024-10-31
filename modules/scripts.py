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
    emotions = SQL_request("SELECT mood FROM users WHERE id = ?", (user_id,))
    print(emotions)
    if emotions != (None,):
        emotions = json.loads(emotions[0])
        if result and result[0]:
            mood_data = json.loads(result[0])
            if date in mood_data:
                moods = [entry['mood'] for time, entry in mood_data[date].items()]
                mood_message = "    ".join(
                    next((emoji for emoji, text in emotions.items() if text.lower() == mood.lower()), mood)
                    for mood in moods
                )
                mood_message = format_emojis(mood_message)
                return mood_message
            else:
                return "Нет записей настроений"
        else:
            return "Данные о настроении отсутствуют"
    else:
        return "Данные о настроении отсутствуют"

def format_emojis(text):  # Разделяем текст на смайлики
    emojis = text.split()
    emojis = emojis[:20]
    rows = []
    for i in range(5):
        row = '    '.join(emojis[i*4:(i+1)*4])
        rows.append(row)
    result = '\n'.join(rows)
    return result

def edit_value(user_id, edit, smile, text):
    text = text.replace(" ", "")
    result = SQL_request("SELECT mood FROM users WHERE id = ?", (user_id,))
    emotions = json.loads(result[0])
    emotions[smile] = text
    updated_emotions = json.dumps(emotions, ensure_ascii=False)
    SQL_request("UPDATE users SET mood = ? WHERE id = ?", (updated_emotions, user_id))
    return f"Настроение изменено!"

def delete_value(user_id, smile):
    result = SQL_request("SELECT mood FROM users WHERE id = ?", (user_id,))
    emotions = json.loads(result[0])
    if smile in emotions:
        emotions.pop(smile)
        updated_emotions = json.dumps(emotions, ensure_ascii=False)
        SQL_request("UPDATE users SET mood = ? WHERE id = ?", (updated_emotions, user_id))
        return f"Запись с {smile} удалена!"
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


# ПРОВЕРКА СОЗДАНИЯ БД
if not os.path.exists(DB_PATH):
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER,
            message INTEGER, 
            frends INTEGER,
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

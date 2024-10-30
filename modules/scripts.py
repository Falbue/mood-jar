import json
from datetime import datetime
import pytz
import sqlite3
import os

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))  # текущая директория скрипта
SCRIPT_DIR = os.path.dirname(PARENT_DIR)  # директория уровнем выше
DB_NAME = 'database.db'
DB_PATH = f"{SCRIPT_DIR}/{DB_NAME}"
VERSION = "test"

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
    result = SQL_request("SELECT mood FROM users WHERE id = ?", (user_id,))
    if result and result[0]:
        mood_data = json.loads(result[0])
    else:
        mood_data = {}
    if current_date not in mood_data:
        mood_data[current_date] = {}
    if len(mood_data[current_date]) < 20:
        mood_data[current_date][current_time] = {'mood': mood, 'reason': reason}
    else:
        print("Достигнуто максимальное количество записей на текущий день")
        return
    
    # Обновление записи в базе данных
    SQL_request("UPDATE users SET mood = ? WHERE id = ?", (json.dumps(mood_data, ensure_ascii=False), user_id))

def get_only_mood(user_id, date):  # Извлекаем данные настроений для пользователя из базы данных
    result = SQL_request("SELECT mood FROM users WHERE id = ?", (user_id,))
    if result and result[0]:
        mood_data = json.loads(result[0])
        if date in mood_data:
            moods = [entry['mood'] for time, entry in mood_data[date].items()]
            mood_message = "    ".join(moods)
            return mood_message
        else:
            return f"Нет записей настроений за {date}"
    else:
        return "Данные о настроении отсутствуют для данного пользователя"

def format_emojis(text):  # Разделяем текст на смайлики
    emojis = text.split()
    emojis = emojis[:20]
    rows = []
    for i in range(5):
        row = '    '.join(emojis[i*4:(i+1)*4])
        rows.append(row)
    result = '\n'.join(rows)
    return result

# ПРОВЕРКА СОЗДАНИЯ БД
if not os.path.exists(DB_PATH):
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER,
            message INTEGER, 
            frend INTEGER,
            time_registration TIME,
            username TEXT,
            topics TEXT,
            mood JSON
        )
    """)
    connect.commit()
    connect.close()
    print("База данных создана")

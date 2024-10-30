from datetime import datetime, timedelta
import pytz
import sqlite3
import os

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))  # текущая директория скрипта
SCRIPT_DIR = os.path.dirname(PARENT_DIR)  # директория уровнем выше
DB_NAME = 'database.db'
DB_PATH = f"{SCRIPT_DIR}/{DB_NAME}"
VERSION = "test"




def now_time():  # функция получения текущего времени по мск
    now = datetime.now()
    tz = pytz.timezone('Europe/Moscow')
    now_moscow = now.astimezone(tz)
    current_time = now_moscow.strftime("%H:%M")
    current_date = now_moscow.strftime("%m.%d.%Y")
    date = f"{current_date} {current_time}"
    return date


def SQL_request(request, params=()):  # sql запросы
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



# ПРОВЕРКИ
if os.path.exists(DB_PATH):
    pass
else:
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER,
            message INTEGER, 
            frend INTEGER,
            time_registration TIME,
            username TEXT,
            mood JSON
        )
    """)
    connect.commit()
    connect.close()
    print(f"База данных создана")

from bot_modules.scripts import *

def registration(message):
    user_id = message.chat.id
    message_id = message.message_id
    username = message.from_user.username

    date, time  = now_time()
    user = SQL_request("SELECT 0 FROM users WHERE id = ?", (user_id,))
    if user is None:
        mood = {"😊":"Радость", "😢":"Грусть", "😐":"Равнодушие", "😁":"Восторг", "😴":"Усталость"}
        topics = {"1": "Партнёр", "2": "Работа", "3": "Учёба", "4": "Здоровье", "5": "Друзья"}
        mood_json = json.dumps(mood, ensure_ascii=False)
        topics_json = json.dumps(topics, ensure_ascii=False)
        SQL_request("""INSERT INTO users (id, message, time_registration, mood, topics)
                          VALUES (?, ?, ?, ?, ?)""", (user_id, message_id+1, date, mood_json, topics_json))
        print(f"Зарегистрирован новый пользователь")
    else:
        menu_id = SQL_request("SELECT message FROM users WHERE id = ?", (user_id,))
        SQL_request("""UPDATE users SET message = ?, username = ? WHERE id = ?""", (message_id+1, username, user_id))  # добавление id нового меню
        return menu_id

def info(user):
    user_id = user[0]
    frend = user[2]
    if frend is None:
        frend = "Отсутсвует"
    registration = user[3]
    text = f"""*Ваш id:* {user_id}
Добавленный друг: {frend}
Время регистрации: {registration}
    """
    return text
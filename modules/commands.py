from modules.scripts import *

def registration(message):
    user_id = message.chat.id
    message_id = message.message_id
    username = message.from_user.username

    times = now_time()
    user = SQL_request("SELECT 0 FROM users WHERE id = ?", (user_id,))
    if user is None:
        SQL_request("""INSERT INTO users (id, message, time_registration)
                          VALUES (?, ?, ?)""", (user_id, message_id+1, times))
        print(f"Зарегистрирован новый пользователь")
    else:
        menu_id = SQL_request("SELECT message FROM users WHERE id = ?", (user_id,))
        SQL_request("""UPDATE users SET message = ?, username = ? WHERE id = ?""", (message_id+1, username, user_id))  # добавление id нового меню
        return menu_id

def profile(user):
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
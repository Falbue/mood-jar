# mood-jar
**Mood Jar** — это Telegram бот, интергированный с веб-приложением для отслеживания и сохранения настроений. Telegram бот позволяет пользователям записывать свое настроение, что помогает анализировать эмоциональное состояние и улучшать осознанность
## Возможности
- Запись и сохранение настроений с метками и комментариями
- Возможность просмотра истории настроений
- Визуализация изменений настроений на графике
- Поддержка анонимного использования или входа через аккаунт
## Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Falbue/mood-jar.git
   ```
2. Перейдите в папку проекта:
   ```bash
   cd mood-jar
   ```
3. Установите зависимости:
  ```bash
pip install -r requirements.txt
```
4. Создайте файл `config.py`:
   ```python
   API = ''  # API бота
   ADMIN = '' # id пользователя телеграм, который будет администратором бота
   ```
6. Запустите приложение:
   ```bash
   python bot.py
   ```
   
## Использование
После запуска бота, перейдите в Telegram, в вашего бота, и введите `/start`
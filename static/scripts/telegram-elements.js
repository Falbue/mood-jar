window.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram.WebApp;
    tg.expand(); // Растягивает приложение на весь экран

    // Пример получения информации о пользователе
    const user = tg.initDataUnsafe?.user;
    if (user) {
        document.getElementById('user-info').textContent = `Привет, ${user.first_name}!`;
    }

    // Устанавливаем кнопку "Закрыть"
    tg.MainButton.text = "Закрыть";
    tg.MainButton.show();
    tg.MainButton.onClick(() => tg.close());
});

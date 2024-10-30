// Параметры физики для настройки
const GRAVITY = 0.05; // сила притяжения
const FRICTION = 0.98; // замедление, чтобы уменьшить скорость со временем
const BOUNCE = 0.3; // коэффициент отскока
const TILT_SENSITIVITY = 0.05; // определяет, насколько сильно шарик реагирует на наклон

const balls = [];

function createBall() {
    const ball = document.createElement('div');
    ball.classList.add('ball');
    document.body.appendChild(ball);

    // Начальные параметры для каждого шарика
    const ballObj = {
        element: ball,
        x: window.innerWidth / 2,
        y: window.innerHeight / 2,
        velocityX: 0,
        velocityY: 0
    };
    balls.push(ballObj);
}

function updatePhysics() {
    balls.forEach(ball => {
        // Применяем гравитацию и трение
        ball.velocityY += GRAVITY;
        ball.velocityX *= FRICTION;
        ball.velocityY *= FRICTION;

        // Обновляем позицию
        ball.x += ball.velocityX;
        ball.y += ball.velocityY;

        // Проверка столкновений с краями экрана
        if (ball.x <= 0 || ball.x + 50 >= window.innerWidth) {
            ball.velocityX *= -BOUNCE; // Отскок по x
            ball.x = Math.max(0, Math.min(ball.x, window.innerWidth - 50));
        }

        if (ball.y <= 0 || ball.y + 50 >= window.innerHeight) {
            ball.velocityY *= -BOUNCE; // Отскок по y
            ball.y = Math.max(0, Math.min(ball.y, window.innerHeight - 50));
        }

        // Обновляем позицию элемента
        ball.element.style.left = `${ball.x}px`;
        ball.element.style.top = `${ball.y}px`;
    });
    requestAnimationFrame(updatePhysics);
}

// Начальное создание одного шарика
createBall();
updatePhysics();

// Обработка наклона устройства
window.addEventListener('deviceorientation', (event) => {
    const tiltX = event.gamma; // Наклон влево/вправо
    const tiltY = event.beta;  // Наклон вперёд/назад

    balls.forEach(ball => {
        // Изменяем скорость в зависимости от наклона
        ball.velocityX += tiltX * TILT_SENSITIVITY;
        ball.velocityY += tiltY * TILT_SENSITIVITY;
    });
});
const API_BASE_URL = 'http://127.0.0.1:9000'; // перед деплоем не забудьте поменять сыллку

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('register-link').addEventListener('click', showRegisterForm);
    document.getElementById('login-link').addEventListener('click', showLoginForm);
    document.getElementById('current-user-link').addEventListener('click', getCurrentUser);
    document.getElementById('logout-link').addEventListener('click', logoutUser);
    document.getElementById('home-link').addEventListener('click', showHomePage);
    document.getElementById('update-profile-link').addEventListener('click', showUpdateProfileForm);
    document.getElementById('basket-link').addEventListener('click', function(event) {
    event.preventDefault();
    viewBasket();
});
    showHomePage();
    checkauthorization();
});

let userId = null;

function showUpdateProfileForm(event) {
    event.preventDefault();  // Останавливаем переход по ссылке

    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Обновление профиля</h2>
        <form id="update-profile-form">
            <label for="name">Имя:</label>
            <input type="text" id="name" name="name" required><br>

            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required><br>

            <label for="password">Пароль:</label>
            <input type="password" id="password" name="password" required>
            <button type="button" id="toggle-password">Показать пароль</button><br>

            <label for="confirm-password">Подтвердите пароль:</label>
            <input type="password" id="confirm-password" name="confirm-password" required><br>

            <button type="submit">Обновить профиль</button>
        </form>
    `;

    // Добавляем обработчик для показа/скрытия пароля
    document.getElementById('toggle-password').addEventListener('click', togglePasswordVisibility);

    // Загружаем текущие данные пользователя
    loadUserProfile();

    // Добавляем обработчик отправки формы
    document.getElementById('update-profile-form').addEventListener('submit', updateUserProfile);
}

function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const toggleButton = document.getElementById('toggle-password');

    // Переключаем тип инпутов пароля между 'password' и 'text'
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        confirmPasswordInput.type = 'text';
        toggleButton.textContent = 'Скрыть пароль';
    } else {
        passwordInput.type = 'password';
        confirmPasswordInput.type = 'password';
        toggleButton.textContent = 'Показать пароль';
    }
}

function loadUserProfile() {
    fetch(`${API_BASE_URL}/user/current-user`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        // Сохраняем user_id
        userId = data.id;  // Получаем и сохраняем id пользователя

        // Заполняем поля формы текущими данными пользователя
        document.getElementById('name').value = data.name;
        document.getElementById('email').value = data.email;
    })
    .catch(error => {
        console.error('Ошибка загрузки профиля:', error);
        document.getElementById('content').innerHTML = '<p>Ошибка при загрузке профиля. Пожалуйста, попробуйте снова.</p>';
    });
}

function updateUserProfile(event) {
    event.preventDefault();  // Останавливаем перезагрузку страницы при отправке формы

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Проверяем, совпадают ли пароли
    if (password !== confirmPassword) {
        alert('Пароли не совпадают. Пожалуйста, попробуйте снова.');
        return;
    }

    // Собираем данные для отправки
    const userData = {
        name: name,
        email: email,
        password: password  // Отправляем открытый пароль, как указано
    };

    // Логируем данные, которые отправляются на сервер, для отладки
    console.log("Отправляемые данные:", userData);

    // Отправляем запрос на сервер для обновления данных, используя user_id
    fetch(`${API_BASE_URL}/user/update_user/${userId}`, {  // Используем динамический user_id
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(userData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                console.error("Ошибка при обновлении профиля:", data);
                alert('Произошла ошибка при обновлении профиля. Пожалуйста, попробуйте снова.');
            });
        }
        return response.json();
    })
    .then(data => {
        alert('Профиль успешно обновлён!');
        showHomePage();  // После обновления вернём пользователя на главную
    })
    .catch(error => {
        console.error('Ошибка при обновлении профиля:', error);
        alert('Произошла ошибка при обновлении профиля. Пожалуйста, попробуйте снова.');
    });
}

function checkauthorization() {
    fetch(`${API_BASE_URL}/user/current-user`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => {
        if (response.ok) {
            // Пользователь авторизован, показываем кнопки профиля и выхода
            document.getElementById('register-link').style.display = 'none';
            document.getElementById('login-link').style.display = 'none';
            document.getElementById('current-user-link').style.display = 'inline';
            document.getElementById('logout-link').style.display = 'inline';
            document.getElementById('basket-link').style.display = 'inline';
            document.getElementById('update-profile-link').style.display = 'inline';
        } else {
            // Пользователь не авторизован, показываем кнопки входа и регистрации
            document.getElementById('register-link').style.display = 'inline';
            document.getElementById('login-link').style.display = 'inline';
            document.getElementById('current-user-link').style.display = 'none';
            document.getElementById('logout-link').style.display = 'none';
            document.getElementById('basket-link').style.display = 'none';
            document.getElementById('update-profile-link').style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Ошибка при проверке авторизации:', error);
        document.getElementById('register-link').style.display = 'inline';
        document.getElementById('login-link').style.display = 'inline';
        document.getElementById('current-user-link').style.display = 'none';
        document.getElementById('logout-link').style.display = 'none';
    });
}

function getCurrentUser(event) {
    event.preventDefault();
    fetch(`${API_BASE_URL}/user/current-user`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(errorText => {
                console.error("Ошибка при получении профиля: ", errorText);
                document.getElementById('content').innerHTML = '<p>Произошла ошибка при получении профиля. Пожалуйста, войдите в систему.</p>';
            });
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data) {
            const content = document.getElementById('content');
            content.innerHTML = `
                <h2>Мой профиль</h2>
                <p>Имя: ${data.name}</p>
                <p>Email: ${data.email}</p>
            `;
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

function showHomePage(event) {
    if (event) event.preventDefault();
    console.log('Переход на главную страницу');
    fetchProducts();
}

function showRegisterForm(event) {
    event.preventDefault();
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Регистрация</h2>
        <form id="register-form">
            <label>Имя: <input type="text" name="name" required></label><br>
            <label>Email: <input type="email" name="email" required></label><br>
            <label>Пароль: <input type="password" name="password" required></label><br>
            <button type="submit">Зарегистрироваться</button>
        </form>
    `;
    document.getElementById('register-form').addEventListener('submit', registerUser);
}

function showLoginForm(event) {
    event.preventDefault();
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Вход</h2>
        <form id="login-form">
            <label>Username: <input type="text" name="username" required></label><br>
            <label>Email: <input type="email" name="email" required></label><br>
            <label>Пароль: <input type="password" name="password" required></label><br>
            <button type="submit">Войти</button>
        </form>
    `;
    document.getElementById('login-form').addEventListener('submit', loginUser);
}

function registerUser(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    fetch(`${API_BASE_URL}/user/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: formData.get('name'),
            email: formData.get('email'),
            password: formData.get('password')
        })
    })
    .then(response => response.json())
    .then(data => {
        alert('Регистрация прошла успешно!');
        location.reload();  // Обновляем страницу
        showLoginForm();  // Перенаправляем на страницу входа
    })
    .catch(error => console.error('Error:', error));
}

function loginUser(event) {
    event.preventDefault();

    const username = document.querySelector('input[name="username"]').value;
    const email = document.querySelector('input[name="email"]').value;
    const password = document.querySelector('input[name="password"]').value;

    fetch(`${API_BASE_URL}/user/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password,
            email: email,
        }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.auth_token) {
            alert('Вход успешен!');
            showHomePage();
        } else {
            alert('Ошибка при входе: ' + data.detail);
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

function logoutUser(event) {
    event.preventDefault();
    fetch(`${API_BASE_URL}/user/logout`, {
        method: 'POST',
        credentials: 'include'
    })
    .then(response => {
        if (response.ok) {
            alert('Вы успешно вышли из системы!');
            showHomePage();
        } else {
            alert('Ошибка при выходе.');
        }
    })
    .catch(error => console.error('Error:', error));
}

// products
function fetchProducts() {
    fetch(`${API_BASE_URL}/app/product`, {
        method: 'GET',
        credentials: 'include',
    })
    .then(response => response.json())
    .then(data => {
        console.log('Полученные данные:', data); // Для отладки

        // Теперь используем поле `data`, которое содержит массив продуктов
        const products = data.data;

        if (!Array.isArray(products)) {
            console.error('Ошибка: Ожидаемый массив данных, но пришло что-то другое.');
            return;
        }

        const content = document.getElementById('content');
        let productCards = '<h2>Все продукты</h2>';

        products.forEach(product => {
            productCards += `
                <div class="product-card">
                    <img src="${product.product_image}" alt="${product.name} - тут должна быть ссылка на изображение" style="max-width: 200px; max-height: 200px;" />
                    <h3>${product.name}</h3>
                    <p>Цена: ${product.price}</p>
                    <p>Описание: ${product.description}</p>
                    <label for="quantity-${product.id}">Количество:</label>
                    <input type="number" id="quantity-${product.id}" name="quantity" min="1" value="1">
                    <button onclick="addToBasket(${product.id}, ${product.price})">Добавить в корзину</button>
                </div>
            `;
        });

        content.innerHTML = productCards;
        console.log('Продукты успешно загружены');
    })
    .catch(error => {
        console.error('Ошибка при загрузке продуктов:', error);
    });
}



// basket
// Функция для получения basket_id
function getOrCreateBasketId() {
    return fetch(`${API_BASE_URL}/app/basket/`, {  // Обратите внимание на завершающий слэш
        method: 'POST',  // Поскольку запрос создаёт или получает корзину, используем метод POST
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка получения или создания basket_id: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('Полученные данные:', data);  // Для отладки выводим весь ответ
        const basketId = data.id;  // Извлекаем basket_id из ответа
        console.log('basket_id:', basketId);  // Выводим basket_id для проверки
        return basketId;
    })
    .catch(error => {
        console.error('Ошибка при получении или создании basket_id:', error);
        return null;  // Возвращаем null, если произошла ошибка
    });
}

// Функция для добавления товара в корзину
function addToBasket(productId, productPrice) {
    const quantity = document.getElementById(`quantity-${productId}`).value;

    // Сначала получаем или создаем basket_id
    getOrCreateBasketId().then(basketId => {
        if (!basketId) {
            console.error('Ошибка: basket_id не найден');
            return;
        }

        // Используем полученный basket_id для добавления товара в корзину
        fetch(`${API_BASE_URL}/app/basket/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                product_id: productId,
                price: productPrice,
                quantity: parseInt(quantity),
                basket_id: basketId  // Используем полученный basket_id
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Ответ от сервера:', data);  // Для отладки выводим ответ сервера
            alert('Продукт добавлен в корзину');
        })
        .catch(error => {
            console.error('Ошибка при добавлении в корзину:', error);
        });
    });
}

// Функция для получения basket_id пользователя
function getBasketId() {
    return fetch(`${API_BASE_URL}/app/basket/user-basket-id`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        return data.basket_id;  // Возвращаем basket_id
    })
    .catch(error => {
        console.error('Ошибка при получении basket_id:', error);
        return null;
    });
}

// Функция для отображения содержимого корзины
function viewBasket() {
    console.log('Basket page');
    // Сначала получаем basket_id для текущего пользователя
    getBasketId().then(basketId => {
        if (!basketId) {
            console.error('Ошибка: basket_id не найден');
            return;
        }

        // Запрашиваем содержимое корзины с этим basket_id
        fetch(`${API_BASE_URL}/app/basket/${basketId}`, {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка при получении данных корзины');
            }
            return response.json();
        })
        .then(data => {
            const content = document.getElementById('content');
            let basketItems = '<h2>Корзина</h2>';

            if (data.basket_items.length === 0) {
                basketItems += '<p>Корзина пуста</p>';
            } else {
                data.basket_items.forEach(item => {
                    basketItems += `
                        <div class="basket-item">
                            <h3>${item.product.name}</h3>
                            <p>Цена за единицу: ${item.product.price}</p>
                            <p>Количество: <input type="number" id="item-quantity-${item.id}" value="${item.quantity}" min="1"></p>
                            <button onclick="updateBasketItem(${item.id})">Обновить количество</button>
                            <button onclick="removeFromBasket(${item.id})">Удалить</button>
                        </div>
                    `;
                });

                basketItems += `
                    <p>Общая стоимость: ${data.total_price.toFixed(2)} ₽</p>  <!-- Вывод общей стоимости -->
                    <button onclick="checkout()">Оформить заказ</button>
                    <button onclick="clearBasket()">Очистить корзину</button>
                `;
            }

            content.innerHTML = basketItems;
        })
        .catch(error => {
            console.error('Ошибка при загрузке корзины:', error);
        });
    });
}


// Функция для обновления количества товара в корзине
function updateBasketItem(itemId, basketId) {
    const quantity = parseInt(document.getElementById(`item-quantity-${itemId}`).value);

    console.log('Отправляемые данные:', {
        quantity: quantity,
        basket_id: basketId
    });

    fetch(`${API_BASE_URL}/app/basket/items/${itemId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
            quantity: quantity,
            basket_id: basketId  // Указываем basket_id для обновления в нужной корзине
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка при обновлении товара в корзине');
        }
        return response.json();
    })
    .then(data => {
        alert('Количество обновлено');
        viewBasket();  // Обновляем отображение корзины после изменения
    })
    .catch(error => {
        console.error('Ошибка при обновлении товара в корзине:', error);
    });
}


function removeFromBasket(itemId) {
    const quantity = 1;

    fetch(`${API_BASE_URL}/app/basket/items/${itemId}?quantity=${quantity}`, {
        method: 'DELETE',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        alert('Продукт удален из корзины');
        viewBasket();
    })
    .catch(error => {
        console.error('Ошибка при удалении продукта из корзины:', error);
    });
}

function clearBasket() {
    fetch(`${API_BASE_URL}/app/basket`, {
        method: 'DELETE',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        alert('Корзина очищена');
        viewBasket();
    })
    .catch(error => {
        console.error('Ошибка при очистке корзины:', error);
    });
}

function checkout() {
    alert('Дальше идет подлкючение к оплате');  // Заменить на реальную оплату
}

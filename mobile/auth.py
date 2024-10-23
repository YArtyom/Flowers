import requests
import flet as ft
from database import API_BASE_URL, get_current_user


def login_user(username, password, email, page):
    response = requests.post(f"{API_BASE_URL}/user/login", json={
        "username": username,
        "password": password,
        "email": email,
    })
    if response.status_code == 200:
        # Если все хорошо

        # # Сохраняем токен
        token = response.json().get("auth_token")
        # # Сохраняем токен и переходим на страницу с продуктами
        page.client_storage.set("auth_token", token)

        user = get_current_user(token)
        page.client_storage.set("auth_user", user)

        page.go("/products")  # Переход через роутер
    else:
        snack_bar = ft.SnackBar(ft.Text("Ошибка авторизации"), bgcolor="red")
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()


def register_user(username, email, password, confirm_password, page):
    """Функция для регистрации нового пользователя."""
    if password != confirm_password:
        snack_bar = ft.SnackBar(ft.Text("Пароли не совпадают"), bgcolor="red")
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
        return

    response = requests.post(f"{API_BASE_URL}/user/register", json={
        "name": username,
        "password": password,
        "email": email
    })

    if response.status_code == 201:
        # Переход на страницу с продуктами через логин
        login_user(username, password, email, page)
    else:
        snack_bar = ft.SnackBar(ft.Text(f"Ошибка регистрации: {response.json()}"), bgcolor="red")
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()


def logout_user(page):
    """Функция для выхода пользователя."""
    response = requests.post(f"{API_BASE_URL}/user/logout", headers={
        "Authorization": f"Bearer {page.client_storage.get('auth_token')}"
    })
    if response.status_code == 200:
        page.client_storage.remove("auth_user")  # Удаляем пользователя
        page.client_storage.remove("auth_token")  # Удаляем токен
        page.go("/login")  # Переход на страницу логина
        page.update()
    else:
        print("Fail")
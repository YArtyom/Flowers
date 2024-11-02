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
        token = response.json().get("auth_token")
        page.client_storage.set("auth_token", token)
        user = get_current_user(token)
        page.client_storage.set("auth_user", user)
        page.go("/products")
    else:
        snack_bar = ft.SnackBar(ft.Text("Ошибка авторизации"), bgcolor="red")
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

def register_user(username, email, password, confirm_password, page):
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
        login_user(username, password, email, page)
    else:
        snack_bar = ft.SnackBar(ft.Text(f"Ошибка регистрации: {response.json()}"), bgcolor="red")
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

def logout_user(page):
    response = requests.post(f"{API_BASE_URL}/user/logout", headers={
        "Authorization": f"Bearer {page.client_storage.get('auth_token')}"
    })
    if response.status_code == 200:
        page.client_storage.remove("auth_user")
        page.client_storage.remove("auth_token")
        page.go("/login")
        page.update()

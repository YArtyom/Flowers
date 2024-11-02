import flet as ft
import requests
from database import API_BASE_URL, get_current_user
from auth import login_user


# Функции для изменения данных профиля
def update_profile(user, token, page):
    current_user = get_current_user(token)

    print(user['password'])
    """Функция для изменения данных профиля"""
    response = requests.put(
        f"{API_BASE_URL}/user/update_user/{current_user['id']}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": user["name"],
            "email": user["email"],
            # "profile_picture": "string",
            "password": f"{user['password']}"
        },
    )

    if response.status_code == 200:
        # print("Success")
        login_user(user["name"], user["password"], user["email"], page)
        snack_bar = ft.SnackBar(ft.Text("Ваш профиль обновиться после перезагрузки"), bgcolor="green")
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
    else:
        print("Fail")


def show_profile_page(page, user):
    """Функция для отображения страницы профиля с возможностью редактирования"""

    page.clean()
    token = page.client_storage.get("auth_token")

    page.title = "Профиль"

    # Переменные для хранения состояния редактирования
    is_editing = False

    # Статичные текстовые поля
    username_text = ft.Text(f"Логин: {user['name']}", size=24, weight="bold")
    email_text = ft.Text(f"Электронная почта: {user['email']}", size=24, weight="bold")

    # Редактируемые поля
    username_field = ft.TextField(value=user['name'], label="Логин", width=300)
    email_field = ft.TextField(value=user['email'], label="Электронная почта", width=300)
    # current_password_field = ft.TextField(label="Текущий пароль", password=True, width=300)
    new_password_field = ft.TextField(label="Новый пароль", password=True, width=300)

    # Функция для переключения между режимами редактирования и просмотра
    def toggle_edit_mode(e):
        nonlocal is_editing
        is_editing = not is_editing  # Меняем режим

        if is_editing:
            # Показываем редактируемые поля и кнопку "Сохранить"
            page.clean()
            page.add(
                ft.Column([
                    username_field,
                    email_field,
                    # current_password_field,
                    new_password_field,
                    ft.ElevatedButton(text="Сохранить изменения", on_click=save_changes),
                    ft.ElevatedButton(text="Отмена", on_click=toggle_edit_mode),  # Кнопка для отмены изменений
                    ft.ElevatedButton(text="Продукты", on_click=lambda e: page.go("/products")),
                    ft.ElevatedButton(text="Выйти", on_click=lambda e: page.go("/logout"))
                ], width=page.width, spacing=10, alignment="center", horizontal_alignment="center")
            )
        else:
            # Вернуть статичные поля, если отменено
            page.clean()
            page.add(
                ft.Column([
                    username_text,
                    email_text,
                    ft.ElevatedButton(text="Изменить профиль", on_click=toggle_edit_mode),
                    ft.ElevatedButton(text="Продукты", on_click=lambda e: page.go("/products")),
                    ft.ElevatedButton(text="Выйти", on_click=lambda e: page.go("/logout"))
                ], width=page.width, spacing=10, alignment="center", horizontal_alignment="center")
            )
        page.update()

    def save_changes(e):
        """Сохраняем изменения профиля"""
        new_username = username_field.value
        new_email = email_field.value
        # current_password = current_password_field.value
        new_password = new_password_field.value

        update_profile({"name": new_username, "email": new_email, "password": new_password}, token, page)

        # Обновляем текстовые поля после сохранения
        username_text.value = f"Логин: {user['name']}"
        email_text.value = f"Электронная почта: {user['email']}"

        # Возвращаемся к просмотру
        toggle_edit_mode(e)

    # Начальный вид страницы с статичными текстовыми полями
    page.add(
        ft.Column([
            username_text,
            email_text,
            ft.ElevatedButton(text="Изменить профиль", on_click=toggle_edit_mode),
            ft.ElevatedButton(text="Продукты", on_click=lambda e: page.go("/products")),
            ft.ElevatedButton(text="Выйти", on_click=lambda e: page.go("/logout"))
        ], width=page.width, spacing=10, alignment="center", horizontal_alignment="center")
    )

    page.update()
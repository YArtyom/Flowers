import flet as ft
from auth import login_user, register_user, logout_user
from database import get_current_user
from profile import show_profile_page
from payment_page import get_payment_page
from orders import get_orders_page
from products import show_products_page


def main(page: ft.Page):
    """Главная функция приложения с навигацией между логином и регистрацией."""

    # Функции для переключения между страницами
    def route_change(route):
        page.clean()  # Очищаем страницу перед изменением маршрута

        # # Проверяем токен один раз при изменении маршрута
        token = page.client_storage.get("auth_token")
        user = page.client_storage.get("auth_user")
        # print(token)

        #
        # headers = {}
        # if token:
        #     headers = {"Authorization": f"Token {token}"}

        if not token and page.route != "/login" and page.route != "/register":
            page.go("/login")  # Если токена нет, перенаправляем на логин
            return

        if page.route == "/login":
            render_login_form()
        elif page.route == "/register":
            render_register_form()
        elif page.route == "/logout":
            logout_user(page)
        elif page.route == "/products":
            show_products_page(page)
        elif page.route == "/basket":
            get_orders_page(page, user)
        elif page.route == "/payment":
            get_payment_page(page, user)
        elif page.route == "/profile":
            show_profile_page(page, user)
        else:
            render_initial_buttons()
        page.update()

    # Форма авторизации
    def render_login_form():
        page.clean()
        login_username = ft.TextField(label="Логин")
        login_password = ft.TextField(label="Пароль", password=True)
        login_email = ft.TextField(label="Электронная почта")
        login_button = ft.ElevatedButton(
            text="Войти",
            on_click=lambda e: login_user(login_username.value, login_password.value, login_email.value, page)
        )

        page.add(
            ft.Column([
                ft.Text("Форма авторизации", size=20),
                login_username,
                login_password,
                login_email,
                login_button,
                ft.ElevatedButton(text="Зарегистрироваться", on_click=lambda _: page.go("/register"))  # Переход на регистрацию
            ])
        )

    # Форма регистрации
    def render_register_form():
        page.clean()
        register_username = ft.TextField(label="Логин")
        register_email = ft.TextField(label="Электронная почта")
        register_password = ft.TextField(label="Пароль", password=True)
        register_confirm_password = ft.TextField(label="Подтвердите пароль", password=True)
        register_button = ft.ElevatedButton(text="Зарегистрироваться", on_click=lambda e: register_user(
            register_username.value,
            register_email.value,
            register_password.value,
            register_confirm_password.value,
            page))

        page.add(
            ft.Column([
                ft.Text("Форма регистрации", size=20),
                register_username,
                register_email,
                register_password,
                register_confirm_password,
                register_button,
                ft.ElevatedButton(text="Войти", on_click=lambda _: page.go("/login"))  # Переход на логин
            ])
        )

    # Начальный экран с выбором
    def render_initial_buttons():
        page.add(
            ft.Column([
                ft.Text("Выберите действие", size=20),
                ft.ElevatedButton(text="Войти", on_click=lambda _: page.go("/login")),  # Переход на логин
                ft.ElevatedButton(text="Зарегистрироваться", on_click=lambda _: page.go("/register"))  # Переход на регистрацию
            ])
        )

    page.on_route_change = route_change

    # Проверяем наличие токена при первом запуске
    if page.client_storage.get("auth_token"):
        page.go("/products")  # Если токен есть, сразу переходим на продукты
    else:
        page.go("/login")  # Если токена нет, переходим на логин

    # Стартуем с текущего маршрута
    page.go(page.route)


# Запуск приложения
ft.app(target=main)
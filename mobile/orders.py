import flet as ft
import requests
from database import API_BASE_URL
from baskets import get_current_user_basket_id


def get_orders_page(page, user):
    page.clean()

    token = page.client_storage.get("auth_token")
    headers = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}

    basket = get_current_user_basket_id(headers)
    basket_items = basket['basket_items']

    def increase_basket_item(item):
        """Функция для увеличения количества."""
        response = requests.post(f"{API_BASE_URL}/app/basket/items", headers=headers, json={
            "price": 0,
            "quantity": 1,
            "product_id": item['product']['id'],
            "basket_id": basket['id']
        })
        if response.status_code == 201:
            print(f"Количество продукта '{item['product']['name']}'увеличено")
            render_basket_items()
        else:
            print("Fail")

    def decrease_basket_item(item):
        """Функция для уменьшения количества."""
        response = requests.delete(f"{API_BASE_URL}/app/basket/items/{item['id']}", headers=headers)
        if response.status_code == 200:
            render_basket_items()
        else:
            print("Fail")

    def remove_from_basket(item):
        """Функция для удаления продукта из корзины."""
        response = requests.delete(f"{API_BASE_URL}/app/basket/items/{item['id']}?quantity={item['quantity']}",
                                   headers=headers)
        if response.status_code == 200:
            render_basket_items()
        else:
            print("Fail")

    def checkout():
        """Функция для оформления заказа."""
        response = requests.put(f"{API_BASE_URL}/app/basket/checkout", headers=headers)
        if response.status_code == 200:
            empty_basket()
            page.go("/payment")
        else:
            print("Fail")

    def render_basket_items():
        """Функция для отображения обновленного списка корзины."""
        # nonlocal basket, basket_items
        current_basket = get_current_user_basket_id(headers)
        current_basket_items = current_basket['basket_items']

        if not current_basket_items:
            empty_basket()
            return

        basket_list = ft.ListView(
            controls=[
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.ListTile(
                                    leading=ft.Icon(ft.icons.SHOPPING_BASKET),
                                    title=ft.Text(f"Продукт: {item['product']['name']}", size=16, weight="bold"),
                                    subtitle=ft.Text(f"Цена: {item['price'] * item['quantity']}", size=16),
                                ),
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.icons.REMOVE_CIRCLE_OUTLINE,
                                            tooltip="Уменьшить количество",
                                            on_click=lambda e, current_item=item: decrease_basket_item(current_item)
                                        ),
                                        ft.Text(f"Количество: {item['quantity']}"),
                                        ft.IconButton(
                                            icon=ft.icons.ADD_CIRCLE_OUTLINE,
                                            tooltip="Увеличить количество",
                                            on_click=lambda e, current_item=item: increase_basket_item(current_item)
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE_OUTLINE,
                                            tooltip="Удалить товар",
                                            on_click=lambda e, current_item=item: remove_from_basket(current_item)
                                        ),
                                    ],
                                    alignment="end",
                                    spacing=10,
                                ),
                            ]
                        ),
                        padding=ft.padding.all(10),
                    ),
                    margin=ft.margin.symmetric(vertical=5),
                )
                for item in current_basket_items
            ],
            height=page.height - 200,
            spacing=10
        )

        summa = ft.Text(f"Общая сумма: {basket['total_price']}", size=18, weight="bold")

        take_order = ft.Row(
            [
                ft.ElevatedButton(text="Оформить заказ", on_click=lambda e: checkout()),
                ft.ElevatedButton(
                    text="Продолжить покупки",
                    on_click=lambda e: page.go("/products"),
                )
            ]
        )

        page.clean()
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Корзина", size=24, weight="bold"),
                        summa,
                        basket_list,
                        take_order
                    ],
                    spacing=20
                ),
                padding=ft.padding.all(20)
            )
        )
        page.update()

    def empty_basket():
        """Функция для очистки корзины."""
        page.clean()
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Корзина пуста", size=24, weight="bold"),
                        ft.ElevatedButton(
                            text="Сделать покупки",
                            on_click=lambda e: page.go("/products"))
                    ],
                    spacing=20
                ),
                padding=ft.padding.all(20)
            )
        )
        page.update()

    if basket_items:
        render_basket_items()
    else:
        empty_basket()
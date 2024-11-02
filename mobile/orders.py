import base64

import flet as ft
import requests
from io import BytesIO
from database import API_BASE_URL
from baskets import get_current_user_basket_id

def get_orders_page(page, user):
    page.clean()

    token = page.client_storage.get("auth_token")
    headers = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}

    basket = get_current_user_basket_id(headers)

    def increase_basket_item(item):
        """Функция для увеличения количества."""
        response = requests.post(f"{API_BASE_URL}/app/basket/items", headers=headers, json={
            "price": 0,
            "quantity": 1,
            "product_id": item['product']['id'],
            "basket_id": basket['id']
        })
        if response.status_code == 201:
            print(f"Количество продукта '{item['product']['name']}' увеличено")
            render_basket_items()
        else:
            print("Не удалось увеличить количество товара")

    def decrease_basket_item(item):
        """Функция для уменьшения количества."""
        response = requests.delete(f"{API_BASE_URL}/app/basket/items/{item['id']}", headers=headers)
        if response.status_code == 200:
            render_basket_items()
        else:
            print("Не удалось уменьшить количество товара")

    def remove_from_basket(item):
        """Функция для удаления продукта из корзины."""
        response = requests.delete(f"{API_BASE_URL}/app/basket/items/{item['id']}?quantity={item['quantity']}",
                                   headers=headers)
        if response.status_code == 200:
            render_basket_items()
        else:
            print("Не удалось удалить товар из корзины")

    def checkout():
        """Функция для оформления заказа."""
        response = requests.put(f"{API_BASE_URL}/app/basket/checkout", headers=headers)
        if response.status_code == 200:
            empty_basket()
            page.go("/payment")
        else:
            print("Не удалось оформить заказ")

    # def get_product_image(product_id):
    #     """Функция для получения изображения продукта по его ID."""
    #     image_response = requests.get(f"{API_BASE_URL}/app/product/{product_id}/image", headers=headers)
    #     if image_response.status_code == 200:
    #         # Возвращаем данные изображения как Base64, корректно декодированные
    #         image_base64 = base64.b64encode(image_response.content).decode('utf-8')
    #         return f"data:image/jpeg;base64,{image_base64}"
    #     else:
    #         return None  # Если изображение не найдено, возвращаем None

    def render_basket_items():
        """Функция для отображения обновленного списка корзины."""
        nonlocal basket
        current_basket = get_current_user_basket_id(headers)
        basket = current_basket  # Обновляем текущую корзину
        current_basket_items = current_basket['basket_items']
        print(current_basket_items)

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
                                    leading=ft.Image(
                                        src=f"{API_BASE_URL}/app/product/{item['product']['id']}/image",
                                        width=50,
                                        height=200,
                                        fit=ft.ImageFit.COVER
                                    ),
                                    title=ft.Text(f"Продукт: {item['product']['name']}", size=16, weight="bold"),
                                    subtitle=ft.Text(f"Цена: {item['price'] * item['quantity']} UZS", size=16),
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
            height=page.height - 300,  # Динамическая высота
            spacing=10
        )

        # Обновляем текст с общей суммой
        summa = ft.Text(f"Общая сумма: {current_basket['total_price']} UZS", size=18, weight="bold")

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

    if basket and basket['basket_items']:
        render_basket_items()
    else:
        empty_basket()

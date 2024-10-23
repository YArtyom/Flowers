import flet as ft
import requests
from database import API_BASE_URL


# def add_basket_item(basket_id, product, page):
#     """Функция для добавления продукта в корзину."""
#     print("Продукт добавлен")
#     print(product)
#     # Если продукт новый, добавляем его в корзину
#     response = requests.post(f"{API_BASE_URL}/basketItem/", json={
#         "basket_id": basket_id,
#         "product_id": product["id"],
#         "price": product["price"],
#         "quantity": 1  # Добавляем 1 продукт в корзину
#     })
#     if response.status_code == 201:
#         # После успешного добавления товара обновляем цену корзины
#         change_basket_price(basket_id, product["price"])
#         snack_bar = ft.SnackBar(ft.Text(f"Продукт '{product['name']}' добавлен в корзину"), bgcolor="green")
#         page.overlay.append(snack_bar)
#         snack_bar.open = True
#     else:
#         snack_bar = ft.SnackBar(ft.Text("Корзина добавлена"), bgcolor="green")
#         page.overlay.append(snack_bar)
#         snack_bar.open = True


# def create_basket(user, product, page, headers):
#
#     price = 0
#
#     if product:
#         price = product['price']
#
#     """Функция для создания новой корзины."""
#     response = requests.post(f"{API_BASE_URL}/app/basket/", headers=headers)
#     if response.status_code == 200:
#         basket_id = response.json().get("id")
#         # add_basket_item(basket_id, product=product, page=page)
#         return basket_id  # Возвращаем ID созданной корзины
#     else:
#         print(response.json())
#         return None
#
# def change_basket_price(basket_id, price):
#     """Функция для изменения цены корзины."""
#     response = requests.get(f"{API_BASE_URL}/basket/{basket_id}/")
#     if response.status_code == 200:
#         current_price = response.json().get("price")
#         current_price += price
#         res = requests.patch(f"{API_BASE_URL}/basket/{basket_id}/", json={
#             "price": current_price
#         })
#         if res.status_code == 200:
#             print("Цена обновлена успешно")
#         else:
#             print("Ошибка при обновлении цены")
#     else:
#         print(response.json())
#
#
# def check_existing_product_in_basket(basket_id, product_id):
#     """Функция для проверки, есть ли продукт уже в корзине."""
#     response = requests.post(f"{API_BASE_URL}/app/basket/")
#     if response.status_code == 200:
#         basket_items = response.json()
#         for item in basket_items:
#             if item['basket_id'] == basket_id and item['product']['id'] == product_id:
#                 return item  # Возвращаем элемент, если он существует в корзине
#     return None
#
#
# def update_basket_item_quantity(item):
#     """Функция для обновления количества товара в корзине."""
#     new_quantity = item['quantity'] + 1  # Увеличиваем количество на 1
#     response = requests.patch(f"{API_BASE_URL}/basketItem/{item['id']}/", json={
#         "quantity": new_quantity
#     })
#     if response.status_code == 200:
#         print(f"Количество товара обновлено: {new_quantity}")
#     else:
#         print(f"Ошибка при обновлении количества товара: {response.status_code}")


def get_current_user_basket_id(headers):
    """Функция для получения ID текущей корзины пользователя."""
    response = requests.post(f"{API_BASE_URL}/app/basket/", headers=headers)
    if response.status_code == 201:
        baskets = response.json()
        # print(baskets)
        if baskets:
            return baskets  # Предполагаем, что у пользователя есть хотя бы одна корзина
        else:
            print("У пользователя нет корзин. Создаем новую корзину.")
            # return create_basket(user, product=product, page=page, headers=headers)  # Создаем новую корзину, если у пользователя ее нет
    return None


def add_product_to_basket(headers, product, basket, page):
    response = requests.post(f"{API_BASE_URL}/app/basket/items", headers=headers, json={
        "price": 0,
        "quantity": 1,
        "product_id": product['id'],
        "basket_id": basket['id']
    })
    if response.status_code == 201:
        snack_bar = ft.SnackBar(ft.Text(f"Продукт '{product['name']}' добавлен в корзину"), bgcolor="green", duration=1000)
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
    else:
        print("Fail")


def add_to_basket(product, page):
    user = page.client_storage.get("auth_user")
    token = page.client_storage.get("auth_token")

    headers = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}
    """Функция для добавления продукта в корзину."""
    basket = get_current_user_basket_id(headers)
    add_product_to_basket(headers=headers, product=product, basket=basket, page=page)

    # print(basket_id)
    # print(product["id"])
    # Проверяем, есть ли продукт уже в корзине
    # existing_item = check_existing_product_in_basket(basket_id, product["id"])
    #
    # if existing_item:
    #     # Если продукт уже есть в корзине, увеличиваем его количество
    #     update_basket_item_quantity(existing_item)
    #     snack_bar = ft.SnackBar(ft.Text(f"Количество товара '{product['name']}' увеличено"), bgcolor="blue")
    #     page.overlay.append(snack_bar)
    #     snack_bar.open = True
    # else:
    #     print('Start')
    #     add_basket_item(basket_id, product, page)

    page.update()
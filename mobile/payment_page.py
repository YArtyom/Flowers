import flet as ft


def get_payment_page(page, user):
    page.clean()

    page.title = "Оплата"

    success = ft.Container(
        content=ft.Column(
            [
                ft.Text("Оплата прошла успешно", size=24, weight="bold"),
                ft.ElevatedButton(
                    text="Вернуться к продуктам",
                    on_click=lambda _: page.go("/products"),
                ),
            ]
        ),
    )
    fail = ft.Text("Оплата не прошла", size=24, weight="bold")

    def check():
        page.clean()
        page.add(success)
        page.update()

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("Оплата", size=20, weight="bold"),
                    ft.ElevatedButton(
                        text="Оплатить",
                        on_click=lambda _: check(),
                    ),
                ]
            ),
            padding=ft.padding.all(20),
        )
    )

    page.update()
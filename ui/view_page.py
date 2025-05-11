import flet as ft

def create_view_page(page: ft.Page, image_stack_left, image_stack_right):
    # Функция для возврата в основной режим
    def back_to_main(e):
        page.go("/")

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_BACK,
        tooltip="Вернуться назад",
        on_click=back_to_main
    )

    # Макет 2 (режим просмотра)
    layout2 = ft.Column([
        ft.Row([
            ft.Text("Режим просмотра", size=24, weight=ft.FontWeight.BOLD, expand=True),
            back_button
        ]),
        ft.Row([
            ft.Container(
                content=image_stack_left,
                expand=True,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=5
            ),
            ft.Container(
                content=image_stack_right,
                expand=True,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=5
            )
        ], expand=True)
    ], expand=True)

    return layout2 
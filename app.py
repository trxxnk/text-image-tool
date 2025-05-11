import flet as ft
from ui.main_page import create_main_page
from ui.view_page import create_view_page

def main(page: ft.Page):
    # Настройка страницы
    page.title = "Обработка изображений"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # Создаем компоненты страниц
    layout1, image_stack_left, image_stack_right = create_main_page(page)
    layout2 = create_view_page(page, image_stack_left, image_stack_right)

    # Определение маршрутов для навигации
    def route_change(e):
        page.views.clear()
        
        if e.route == "/":
            page.views.append(
                ft.View(
                    route="/",
                    controls=[
                        ft.AppBar(title=ft.Text("Ввод граничных точек"), center_title=True),
                        layout1
                    ],
                    padding=ft.padding.all(20)
                )
            )
        elif e.route == "/view":
            page.views.append(
                ft.View(
                    route="/view",
                    controls=[
                        ft.AppBar(title=ft.Text("Режим просмотра"), center_title=True),
                        layout2
                    ],
                    padding=ft.padding.all(20)
                )
            )
        
        page.update()

    # Обработчик показа просмотра
    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Инициализация начального вида
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main) 
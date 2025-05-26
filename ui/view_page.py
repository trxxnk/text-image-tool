import flet as ft
from .components.file_pickers import FilePickerManager
from .handlers.picker_handlers import create_save_image_handler


def create_view_page_content(page: ft.Page, image_stack_left:ft.Stack,
                             image_stack_right:ft.Stack):
    """
    Создает содержимое для режима просмотра результата.
    
    Args:
        page: Объект страницы
        image_stack_left: Стек изображения слева
        image_stack_right: Стек изображения справа
        
    Returns:
        Container: Содержимое страницы просмотра
    """
    # Создаем менеджер файловых диалогов
    picker_manager = FilePickerManager(page)

    # Создаем обработчик для сохранения изображения
    image_control = None
    if len(image_stack_right.controls) > 0:
        image_control = image_stack_right.controls[0]
    
    save_image_handler = create_save_image_handler(
        picker_manager, page, image_control
    )

    # Создаем кнопку сохранения изображения
    save_image_button = ft.ElevatedButton(
        "Сохранить изображение",
        on_click=save_image_handler
    )

    # Кнопки управления - размещаем в том же месте для консистентности
    controls_row = ft.Row([
        ft.Container(width=page.width * 0.45), # Пустой контейнер для выравнивания
        ft.Row([
            save_image_button,
        ], spacing=10)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    # Основное содержимое - два изображения рядом
    images_row = ft.Row([
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
    
    # Собираем содержимое
    content = ft.Column([
        controls_row,
        images_row
    ], expand=True)

    return content 
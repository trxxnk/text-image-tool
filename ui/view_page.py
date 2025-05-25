import flet as ft
import os
import cv2


def create_view_page_content(page: ft.Page, image_stack_left:ft.Stack,
                             image_stack_right:ft.Stack):
    """
    Создает содержимое для режима просмотра результата.
    
    Args:
        page: Объект страницы
        workflow_tabs: Вкладки для переключения между режимами
        mode_selector: Селектор режима работы
        image_stack_left: Стек изображения слева
        image_stack_right: Стек изображения справа
        
    Returns:
        Container: Содержимое страницы просмотра
    """
    # Создаем файловый диалог для сохранения изображения
    save_file_picker = ft.FilePicker()
    page.overlay.append(save_file_picker)

    # Функция для сохранения изображения
    def save_image(e):
        def save_image_result(e):
            if e.path:
                try:
                    # Убедимся, что у нас есть изображение для сохранения
                    if hasattr(image_stack_right.controls[0], 'src') and image_stack_right.controls[0].src:
                        # Берем путь из src и сохраняем копию
                        original_path = image_stack_right.controls[0].src.replace('file://', '')
                        new_path = e.path
                        
                        # Создаем директорию если не существует
                        os.makedirs(os.path.dirname(new_path), exist_ok=True)
                        
                        # Сохраняем изображение используя OpenCV
                        img = cv2.imread(original_path)
                        cv2.imwrite(new_path, img)
                        
                        # Показываем уведомление об успехе
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Изображение сохранено в {new_path}"),
                            bgcolor=ft.colors.GREEN
                        )
                        page.snack_bar.open = True
                        page.update()
                except Exception as ex:
                    # Показываем уведомление об ошибке
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Ошибка при сохранении: {str(ex)}"),
                        bgcolor=ft.colors.RED
                    )
                    page.snack_bar.open = True
                    page.update()

        # Открываем диалог сохранения файла
        save_file_picker.on_result = save_image_result
        save_file_picker.save_file(
            allowed_extensions=["png", "jpg", "jpeg", "tif", "tiff"],
            file_name="processed_image.png"
        )

    # Создаем кнопку сохранения изображения
    save_image_button = ft.ElevatedButton(
        "Сохранить изображение",
        on_click=save_image
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
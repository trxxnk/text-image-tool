import flet as ft
import shutil


def handle_save_image(page: ft.Page, image_control: ft.Image):
    """
    Создает обработчик для сохранения изображения.
    
    Args:
        page: Объект страницы
        image_control: Контрол изображения с изображением для сохранения
        
    Returns:
        function: Обработчик для диалога сохранения
    """
    def on_save_click(_):
        def on_save_result(e):
            if e.path:
                try:
                    # Получаем путь к исходному изображению
                    src_path = image_control.src
                    
                    # Если путь начинается с 'data:', значит это встроенное изображение
                    if src_path.startswith('data:'):
                        # Показываем уведомление об ошибке
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text("Невозможно сохранить встроенное изображение"),
                            bgcolor=ft.colors.RED
                        )
                        page.snack_bar.open = True
                        page.update()
                        return
                    
                    # Копируем файл в указанное место
                    shutil.copy2(src_path, e.path)
                    
                    # Показываем уведомление об успешном сохранении
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Изображение сохранено в {e.path}"),
                        bgcolor=ft.colors.GREEN
                    )
                    page.snack_bar.open = True
                    page.update()
                except Exception as ex:
                    # Показываем уведомление об ошибке
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Ошибка при сохранении изображения: {str(ex)}"),
                        bgcolor=ft.colors.RED
                    )
                    page.snack_bar.open = True
                    page.update()
        
        return on_save_result
    
    return on_save_click 
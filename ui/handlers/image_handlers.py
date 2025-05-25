import cv2
import flet as ft
from typing import Callable
from ..state.app_state import AppState
from ..utils.image_utils import add_watermark
from ..components.image_display import ImageDisplay

def process_new_image(file_path: str, state: AppState, image_display: ImageDisplay):
    """Обрабатывает новое изображение"""
    # Сохраняем путь к текущему изображению
    state.current_image_path = file_path
    
    # Сбрасываем флаги
    state.grid_built = False
    state.show_grid = False
    
    # Очищаем точки
    state.clear_points()
    
    # Обновляем изображения для обоих режимов
    image_display.clear()
    
    # Загружаем изображение для получения его размеров
    img = cv2.imread(file_path)
    if img is not None:
        img_height, img_width = img.shape[:2]
        # Вычисляем коэффициент масштабирования
        ratio = img_height / image_display.height
        
        # Устанавливаем изображения
        image_display.set_image(file_path, ratio)

def show_alert(page: ft.Page, message: str):
    """Показывает диалог с предупреждением"""
    def on_click(_):
        page.dialog.open = False # TODO: св-ва page.dialog нет
        page.update()
        
    dlg = ft.AlertDialog(
        title=ft.Text("Предупреждение"),
        content=ft.Text(message),
        actions=[
            ft.TextButton("OK", on_click=on_click)
        ]
    )
    page.dialog = dlg
    dlg.open = True
    page.update()
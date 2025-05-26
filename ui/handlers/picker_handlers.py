import flet as ft
from ..components.file_pickers import FilePickerManager
from .file_handlers import handle_image_upload, handle_save_points, handle_load_points
from ..components.image_display import ImageDisplay
from ..components.control_panel_component import ControlPanelComponent
from ..state.app_state import AppState
from ..utils.image_processor import handle_save_image

def setup_file_picker_handlers(
        picker_manager: FilePickerManager,
        state: AppState,
        image_display: ImageDisplay,
        control_panel: ControlPanelComponent,
        page: ft.Page):
    """
    Настраивает обработчики для FilePickerManager.
    
    Args:
        picker_manager: Менеджер FilePicker'ов
        state: Объект состояния приложения
        image_display: Компонент отображения изображения
        control_panel: Панель управления
        page: Объект страницы
        
    Returns:
        dict: Словарь с обработчиками для кнопок
    """
    # Обработчик для загрузки изображения
    def handle_upload_click(_):
        picker_manager.pick_image(
            handle_image_upload(state, image_display, control_panel, page)
        )
    
    # Обработчик для сохранения точек
    def handle_save_click(_):
        save_handler = handle_save_points(state, page)(_)
        if save_handler:  # Проверяем, что обработчик был создан (т.е. изображение загружено)
            picker_manager.save_points(save_handler)
    
    # Обработчик для загрузки точек
    def handle_load_click(_):
        picker_manager.load_points(
            handle_load_points(state, image_display, control_panel, page)(_)
        )
    
    # Возвращаем словарь с обработчиками
    return {
        "on_upload": handle_upload_click,
        "on_save": handle_save_click,
        "on_load": handle_load_click
    }

def create_image_upload_handler(
        picker_manager: FilePickerManager,
        state: AppState,
        image_display: ImageDisplay,
        control_panel: ControlPanelComponent,
        page: ft.Page):
    """
    Создает обработчик для загрузки изображения.
    
    Args:
        picker_manager: Менеджер FilePicker'ов
        state: Объект состояния приложения
        image_display: Компонент отображения изображения
        control_panel: Панель управления
        page: Объект страницы
        
    Returns:
        function: Обработчик для кнопки загрузки изображения
    """
    def handle_upload_click(_):
        picker_manager.pick_image(
            handle_image_upload(state, image_display, control_panel, page)
        )
    
    return handle_upload_click

def create_save_points_handler(
        picker_manager: FilePickerManager,
        state: AppState,
        page: ft.Page):
    """
    Создает обработчик для сохранения точек.
    
    Args:
        picker_manager: Менеджер FilePicker'ов
        state: Объект состояния приложения
        page: Объект страницы
        
    Returns:
        function: Обработчик для кнопки сохранения точек
    """
    def handle_save_click(_):
        save_handler = handle_save_points(state, page)(_)
        if save_handler:  # Проверяем, что обработчик был создан (т.е. изображение загружено)
            picker_manager.save_points(save_handler)
    
    return handle_save_click

def create_load_points_handler(
        picker_manager: FilePickerManager,
        state: AppState,
        image_display: ImageDisplay,
        control_panel: ControlPanelComponent,
        page: ft.Page):
    """
    Создает обработчик для загрузки точек.
    
    Args:
        picker_manager: Менеджер FilePicker'ов
        state: Объект состояния приложения
        image_display: Компонент отображения изображения
        control_panel: Панель управления
        page: Объект страницы
        
    Returns:
        function: Обработчик для кнопки загрузки точек
    """
    def handle_load_click(_):
        picker_manager.load_points(
            handle_load_points(state, image_display, control_panel, page)(_)
        )
    
    return handle_load_click

def create_save_image_handler(
        picker_manager: FilePickerManager,
        page: ft.Page,
        image_control: ft.Image):
    """
    Создает обработчик для сохранения изображения.
    
    Args:
        picker_manager: Менеджер FilePicker'ов
        page: Объект страницы
        image_control: Контрол изображения
        
    Returns:
        function: Обработчик для кнопки сохранения изображения
    """
    def handle_save_image_click(_):
        if hasattr(image_control, 'src') and image_control.src:
            picker_manager.save_image(
                handle_save_image(page, image_control)(_)
            )
        else:
            # Показываем уведомление об ошибке
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Нет изображения для сохранения"),
                bgcolor=ft.colors.RED
            )
            page.snack_bar.open = True
            page.update()
    
    return handle_save_image_click 
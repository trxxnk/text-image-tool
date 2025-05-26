import flet as ft
from .state.app_state import AppState
from .components.image_display import ImageDisplay
from .components.control_panel_component import ControlPanelComponent
from .components.file_pickers import FilePickerManager
from .handlers.file_handlers import handle_clear
from .handlers.picker_handlers import (
    create_image_upload_handler,
    create_save_points_handler,
    create_load_points_handler
)
from .handlers.grid_handlers import update_grid_if_needed, handle_grid_toggle

def create_main_page_content(page: ft.Page):
    """
    Создает содержимое для режима редактирования/ввода точек.
    
    Args:
        page: Объект страницы
        
    Returns:
        Container: Содержимое страницы редактирования
    """
    # Инициализируем состояние
    state = AppState()
    
    # Константы
    STACK_IMAGE_HEIGHT = page.height * 0.7
    
    # Создаем менеджер FilePicker'ов
    picker_manager = FilePickerManager(page)
    
    # Создаем компонент отображения изображения и панель управления
    # без обработчиков событий, которые будут установлены позже
    image_display = ImageDisplay(
        state=state,
        height=STACK_IMAGE_HEIGHT,
        on_point_added=None  # Установим позже
    )
    
    control_panel = ControlPanelComponent(state=state)
    
    # Функция для обновления сетки при добавлении новой точки
    def handle_point_added():
        control_panel.update_coords_text()
        control_panel.update_button_states()
        update_grid_if_needed(state, image_display, page)
        page.update()
    
    # Устанавливаем обработчик добавления точки
    image_display.on_point_added = handle_point_added
    
    # Создаем обработчики для FilePicker операций
    upload_handler = create_image_upload_handler(
        picker_manager, state, image_display, control_panel, page
    )
    
    save_handler = create_save_points_handler(
        picker_manager, state, page
    )
    
    load_handler = create_load_points_handler(
        picker_manager, state, image_display, control_panel, page
    )
    
    # Создаем обработчик для очистки
    clear_handler = handle_clear(state, image_display, control_panel, page)
    
    # Устанавливаем обработчики событий для панели управления
    control_panel.set_handlers(
        on_upload=upload_handler,
        on_clear=clear_handler,
        on_save=save_handler,
        on_load=load_handler,
        on_grid_toggle=lambda e: handle_grid_toggle(e, state, image_display, page)
    )

    # Основной контент
    content = ft.Row([
        # Левая колонка с изображением
        ft.Container(
            content=image_display.container,
            width=page.width * 0.47,
            height=STACK_IMAGE_HEIGHT,
            alignment=ft.alignment.center
        ),
        
        # Правая колонка с элементами управления
        ft.Column([
            ft.Text("Выберите границу:", size=16),
            control_panel.border_selector,
            ft.Row([
                control_panel.upload_button,
                control_panel.clear_button
            ], spacing=10, wrap=True),
            ft.Row([
                control_panel.save_button,
                control_panel.load_button
            ], spacing=10, wrap=True),
            control_panel.show_grid_checkbox,
            ft.Text("Координаты точек:", size=16),
            control_panel.coords_container,
        ],
            spacing=20,
            width=page.width * 0.5,
            height=STACK_IMAGE_HEIGHT)
    ],
    spacing=20
    )
    
    return content
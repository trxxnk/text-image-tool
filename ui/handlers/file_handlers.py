import flet as ft
from ..utils.file_utils import save_points_to_json, load_points_from_json
from ..components.image_display import ImageDisplay
from ..components.control_panel_component import ControlPanelComponent
from ..state.app_state import AppState
import numpy as np

def handle_image_upload(state: AppState, image_display: ImageDisplay,
                        control_panel: ControlPanelComponent, page: ft.Page):
    """
    Обработчик загрузки изображения.
    
    Args:
        state: Объект состояния приложения
        image_display: Компонент отображения изображения
        control_panel: Панель управления
        page: Объект страницы
    
    Returns:
        Функция-обработчик для FilePicker
    """
    def on_file_result(e):
        if e.files and e.files[0].path:
            image_display.process_new_image(e.files[0].path)
            # Сбрасываем флаги и обновляем чекбокс
            state.show_grid = False
            state.grid_built = False
            state.mesh_canvas = None
            state.clear_points()
            image_display.clear()
            control_panel.show_grid_checkbox.value = False
            control_panel.update_coords_text()
            control_panel.update_button_states()
            page.update()
    return on_file_result

def handle_save_points(state: AppState, page: ft.Page):
    """
    Обработчик сохранения точек.
    
    Args:
        state: Объект состояния приложения
        page: Объект страницы
    
    Returns:
        Функция-обработчик для кнопки сохранения, которая возвращает обработчик FilePicker
    """
    def on_save_click(_):
        def on_save_result(e):
            if e.path:
                try:
                    save_points_to_json(state.edge_points_lists, state.current_image_path, e.path)
                except Exception as e:
                    raise e

        return on_save_result
    return on_save_click

def handle_load_points(state: AppState, image_display: ImageDisplay,
                       control_panel: ControlPanelComponent, page: ft.Page):
    """
    Обработчик загрузки точек из файла.
    
    Args:
        state: Объект состояния приложения
        image_display: Компонент отображения изображения
        control_panel: Панель управления
        page: Объект страницы
    
    Returns:
        Функция-обработчик для кнопки загрузки, которая возвращает обработчик FilePicker
    """
    def on_load_click(_):
        def on_load_result(e):
            if e.files:
                try:
                    load_data = load_points_from_json(e.files[0].path)
                    
                    # Проверяем наличие необходимых данных
                    for edge_name in state.edge_points_lists.keys():
                        if edge_name not in load_data["points"].keys():
                            print(" !! Некорректный формат файла!")
                            return
                    
                    image_display.process_new_image(load_data["image_path"])
                    
                    # Загружаем точки
                    for border, points in load_data["points"].items():
                        state.edge_points_lists[border].extend(points)
                        temp_points = np.array(points, dtype=int) / state.ratio
                        state.points_lists[border].extend(temp_points.tolist())
                        image_display.add_points(temp_points, color=state.colors[border])
                        
                    # Обновляем состояние
                    control_panel.update_coords_text()
                    control_panel.update_button_states()
                    
                    page.update()
                except Exception as e:
                    raise e
        
        return on_load_result
    return on_load_click

def handle_clear(state: AppState, image_display: ImageDisplay,
                 control_panel: ControlPanelComponent, page: ft.Page):
    """
    Обработчик очистки точек.
    
    Args:
        state: Объект состояния приложения
        image_display: Компонент отображения изображения
        control_panel: Панель управления
        page: Объект страницы
    
    Returns:
        Функция-обработчик для кнопки очистки
    """
    def on_clear(_):
        # Очищаем точки в состоянии
        state.clear_points()
        
        # Сбрасываем флаги
        state.grid_built = False
        state.show_grid = False
        
        # Удаляем сетку, если она отображается
        if state.mesh_canvas:
            image_display.remove_mesh_canvas()
            state.mesh_canvas = None
        
        # Очищаем UI
        image_display.clear()
        
        # Обновляем состояние чекбокса
        control_panel.show_grid_checkbox.value = False
        
        # Обновляем UI панели управления
        control_panel.update_coords_text()
        control_panel.update_button_states()
        page.update()
    
    return on_clear 
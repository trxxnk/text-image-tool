import flet as ft
from typing import Callable
from ..state.app_state import AppState

class ControlPanel:
    def __init__(self, state: AppState, on_upload: Callable, on_clear: Callable,
                 on_save: Callable, on_load: Callable, on_grid_toggle: Callable):
        self.state = state
        
        # Создаем выпадающий список для выбора границы
        self.border_selector = ft.Dropdown(
            options=[
                ft.dropdown.Option(key=name, text=name) for name in state.border_names
            ],
            value=state.current_border,
            on_change=self._on_border_changed,
            width=200
        )
        
        # Создаем кнопки (часть из них будем использовать в новом макете)
        self.upload_button = ft.ElevatedButton(
            "Загрузить изображение",
            icon=ft.icons.UPLOAD_FILE,
            on_click=on_upload
        )
        
        self.clear_button = ft.ElevatedButton(
            "Очистить точки",
            icon=ft.icons.DELETE,
            on_click=on_clear
        )
        
        self.save_button = ft.ElevatedButton(
            "Сохранить точки",
            icon=ft.icons.SAVE,
            on_click=on_save,
            disabled=True
        )
        
        self.load_button = ft.ElevatedButton(
            "Загрузить точки",
            icon=ft.icons.UPLOAD_FILE,
            on_click=on_load
        )
        
        # Обновленный чекбокс для построения и отображения сетки
        self.show_grid_checkbox = ft.Checkbox(
            label="Показать сетку",
            value=False,
            on_change=on_grid_toggle,
            disabled=True  # По умолчанию выключен
        )
        
        # Создаем текстовые поля для координат
        self.coords_texts = {
            name: ft.Text(f"{name}: ", size=16, color=state.colors[name])
            for name in state.border_names
        }
        
        # Контейнер с координатами
        self.coords_container = ft.Container(
            content=ft.Column([
                self.coords_texts[name] for name in state.border_names
            ], spacing=5),
            padding=10,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            expand=True
        )
        
        # Собираем все в колонку для старого макета (по прежнему доступно, но не используется в новом макете)
        self.content = ft.Column([
            ft.Text("Управление", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Выберите границу:", size=16),
            self.border_selector,
            ft.Row([
                self.upload_button,
                self.clear_button
            ], spacing=10, wrap=True),
            ft.Row([
                self.save_button,
                self.load_button
            ], spacing=10, wrap=True),
            self.show_grid_checkbox,
            ft.Text("Координаты точек:", size=16),
            self.coords_container
        ], spacing=20, expand=True)
        
    def _on_border_changed(self, e):
        """Обработчик изменения выбранной границы"""
        self.state.current_border = e.control.value
        self.update_coords_text()
        
    def update_coords_text(self):
        """Обновляет текст с координатами"""
        for border, points in self.state.edge_points_lists.items():
            if points:
                coords = ", ".join("({:.0f} , {:.0f})".format(*p) for p in points)
                self.coords_texts[border].value = f"{border}: {coords}"
            else:
                self.coords_texts[border].value = f"{border}: нет точек"
        self.coords_container.update()
                
    def update_button_states(self):
        """Обновляет состояние кнопок и чекбокса"""
        # Проверяем, есть ли хотя бы одна точка в любой границе
        has_any_points = any(len(points) > 0 for points in self.state.points_lists.values())
        
        # Проверяем, есть ли минимум 2 точки в каждой границе
        has_enough_points = all(len(points) >= 2 for points in self.state.points_lists.values())
        
        # Разрешаем сохранение, если есть хотя бы одна точка
        self.save_button.disabled = not has_any_points
        
        # Разрешаем показ/активацию чекбокса только если есть достаточно точек
        self.show_grid_checkbox.disabled = not has_enough_points
        
        # Если недостаточно точек - выключаем чекбокс
        if not has_enough_points and self.show_grid_checkbox.value:
            self.show_grid_checkbox.value = False 
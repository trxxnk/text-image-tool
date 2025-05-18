import flet as ft
from flet import canvas as canv
from typing import Callable, Optional
from ..state.app_state import AppState

class ImageDisplay:
    def __init__(self, state: AppState, height: float, on_point_added: Callable = None):
        self.state = state
        self.height = height
        self.on_point_added = on_point_added
        
        # Создаем компонент изображения
        self.image = ft.Image(
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            height=height
        )
        
        # Stack для наложения точек на изображение
        self.stack = ft.Stack(
            [self.image],
            height=height
        )
        
        # GestureDetector для отслеживания кликов
        self.gesture = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.CLICK,
            content=self.stack,
            on_tap_up=self._handle_image_click,
            height=height
        )
        
        # Контейнер для отображения
        self.container = ft.Container(
            content=self.gesture,
            border=ft.border.all(1, ft.Colors.GREY_400),
            width=None,  # Будет установлено позже
            height=height,
            alignment=ft.alignment.center
        )
        
    def _handle_image_click(self, e: ft.TapEvent):
        if self.image.visible:
            # Получаем координаты клика относительно изображения
            x = e.local_x
            y = e.local_y

            # Создаем точку
            point_radius = 4
            point = ft.Container(
                content=ft.CircleAvatar(
                    bgcolor=self.state.colors[self.state.current_border],
                    radius=point_radius,
                ),  
                left=(x-point_radius),
                top=(y-point_radius)
            )
            
            # Сохраняем координаты в состояние
            self.state.add_point(x, y)
            self.stack.controls.append(point)
            
            # Обновляем UI
            self.stack.update()
            
            # Вызываем callback для обновления панели управления
            if self.on_point_added:
                self.on_point_added()
            
    def set_image(self, image_path: str, ratio: float):
        """Устанавливает новое изображение"""
        self.image.src = image_path
        self.image.visible = True
        self.state.ratio = ratio
        self.stack.update()
        
    def clear(self):
        """Очищает все точки с изображения"""
        self.stack.controls = [self.image]
        self.stack.update()
        
    def add_mesh_canvas(self, canvas: canv.Canvas):
        """Добавляет canvas с сеткой"""
        if canvas not in self.stack.controls:
            # Удаляем старую сетку, если она есть
            for control in self.stack.controls[:]:
                if isinstance(control, canv.Canvas):
                    self.stack.controls.remove(control)
            
            # Добавляем новую сетку
            controls = [self.image, canvas]
            # Добавляем все точки поверх сетки
            controls.extend([c for c in self.stack.controls if c != self.image])
            self.stack.controls = controls
            self.stack.update()
            
    def remove_mesh_canvas(self, canvas: canv.Canvas):
        """Удаляет canvas с сеткой"""
        # Создаем новый список controls без canvas элементов
        self.stack.controls = [control for control in self.stack.controls 
                               if not isinstance(control, canv.Canvas)]
        self.stack.update()
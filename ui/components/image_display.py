import flet as ft
from flet import canvas as canv
import cv2
from typing import Callable, Optional
from ..state.app_state import AppState

class ImageDisplay:
    def __init__(self, state: AppState, height: float, on_point_added: Optional[Callable] = None):
        """
        Инициализирует компонент отображения изображения.
        
        Args:
            state: Объект состояния приложения
            height: Высота компонента
            on_point_added: Обработчик добавления точки (может быть установлен позже)
        """
        self.state = state
        self.height = height
        self._on_point_added = on_point_added
        
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
    
    @property
    def on_point_added(self) -> Optional[Callable]:
        """Геттер для обработчика добавления точки"""
        return self._on_point_added
    
    @on_point_added.setter
    def on_point_added(self, callback: Optional[Callable]):
        """Сеттер для обработчика добавления точки"""
        self._on_point_added = callback
        
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
            if self._on_point_added:
                self._on_point_added()
            
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
        
    def process_new_image(self, file_path: str):
        """Обрабатывает новое изображение"""
        # Сохраняем путь к текущему изображению
        self.state.current_image_path = file_path
        
        # Сбрасываем флаги
        self.state.grid_built = False
        self.state.show_grid = False
        
        # Очищаем точки
        self.state.clear_points()
        
        # Обновляем изображения для обоих режимов
        self.clear()
        
        # Загружаем изображение для получения его размеров
        img = cv2.imread(file_path)
        if img is not None:
            img_height, img_width = img.shape[:2]
            # Вычисляем коэффициент масштабирования
            ratio = img_height / self.height
            
            # Устанавливаем изображения
            self.set_image(file_path, ratio)

        
    def add_points(self, points: list, color:ft.Colors):
        point_radius = 4
        for p in points:
            point = ft.Container(
                content=ft.CircleAvatar(
                    bgcolor=color,
                    radius=point_radius,
                ),
                left=(p[0]-point_radius),
                top=(p[1]-point_radius)
            )
            self.stack.controls.append(point)    
        
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
            
    def remove_mesh_canvas(self):
        """Удаляет canvas с сеткой"""
        # Создаем новый список controls без canvas элементов
        self.stack.controls = [control for control in self.stack.controls 
                               if not isinstance(control, canv.Canvas)]
        self.stack.update()
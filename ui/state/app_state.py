import flet as ft
import numpy as np
from typing import Dict, List, Tuple, Optional

class AppState:
    def __init__(self):
        # Названия границ
        self.border_names = ["edge_top", "edge_bottom", "edge_left", "edge_right"]

        # Списки для хранения точек разных границ
        self.points_lists: Dict[str, List[Tuple[float, float]]] = {name: [] for name in self.border_names}
        self.edge_points_lists: Dict[str, List[Tuple[int, int]]] = {name: [] for name in self.border_names}
        
        # Цвета для границ
        self.colors = {
            "edge_top": ft.Colors.RED,
            "edge_bottom": ft.Colors.BLUE,
            "edge_left": ft.Colors.GREEN,
            "edge_right": ft.Colors.ORANGE
        }
        
        # Текущая выбранная граница
        self.current_border = "edge_top"

        # Флаг для отслеживания успешного построения сетки
        self.grid_built = False
        # Флаг для отображения сетки
        self.show_grid = False

        # Путь к текущему изображению
        self.current_image_path: Optional[str] = None
        
        # Масштаб изображения
        self.ratio: Optional[float] = None
        
        # Canvas для сетки
        self.mesh_canvas = None

    def clear_points(self):
        """Очищает все точки"""
        for border in self.points_lists:
            self.points_lists[border].clear()
            self.edge_points_lists[border].clear()
            
    def check_points(self) -> bool:
        """Проверяет наличие достаточного количества точек"""
        return all(len(points) >= 2 for points in self.points_lists.values())

    def add_point(self, x: float, y: float):
        """Добавляет точку в текущую границу"""
        self.points_lists[self.current_border].append((x, y))
        self.edge_points_lists[self.current_border].append((int(x * self.ratio), int(y * self.ratio)))
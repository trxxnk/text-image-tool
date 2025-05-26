import flet as ft
from flet import canvas as canv
import numpy as np
from ..state.app_state import AppState
from core.utils import build_mesh_function, preprocess_edges

def build_grid(state: AppState) -> tuple[canv.Canvas, canv.Canvas]:
    """Строит сетку на основе точек"""
    # Получаем границы
    edge_top, edge_bottom, edge_left, edge_right = preprocess_edges(**state.points_lists)
    mesh_func = build_mesh_function(edge_top, edge_bottom, edge_left, edge_right)
    
    # Параметры сетки
    n_points = 10
    s_values = np.linspace(0, 1, n_points)
    t_values = np.linspace(0, 1, n_points)
    
    # Создаем сетку параметров
    s_grid, t_grid = np.meshgrid(s_values, t_values)

    # Векторизуем функцию mesh_point
    vectorized_mesh = np.vectorize(lambda s, t: mesh_func(s, t), signature='(),()->(n)')

    # Применяем к сетке параметров
    grid_points: np.ndarray = vectorized_mesh(s_grid, t_grid)
    grid_hlines = grid_points.tolist()
    grid_vlines = grid_points.swapaxes(0, 1).tolist()
    
    # Создание холста для отображения сетки
    edge_width = 3
    edge_top_paint = ft.Paint(stroke_width=edge_width, style=ft.PaintingStyle.STROKE, color=ft.Colors.RED_600)
    edge_bottom_paint = ft.Paint(stroke_width=edge_width, style=ft.PaintingStyle.STROKE, color=ft.Colors.BLUE_600)
    edge_left_paint = ft.Paint(stroke_width=edge_width, style=ft.PaintingStyle.STROKE, color=ft.Colors.GREEN_600)
    edge_right_paint = ft.Paint(stroke_width=edge_width, style=ft.PaintingStyle.STROKE, color=ft.Colors.ORANGE_600)
    
    grid_lines_width = 1
    grid_hlines_paint = ft.Paint(stroke_width=grid_lines_width, style=ft.PaintingStyle.STROKE, color=ft.Colors.BLUE_500)
    grid_vlines_paint = ft.Paint(stroke_width=grid_lines_width, style=ft.PaintingStyle.STROKE, color=ft.Colors.RED_500)
    
    # Создаем canvas для отображения сетки в основном режиме
    mesh_canvas = canv.Canvas(
        [
            canv.Points(edge_top, point_mode=canv.PointMode.POLYGON, paint=edge_top_paint),
            canv.Points(edge_bottom, point_mode=canv.PointMode.POLYGON, paint=edge_bottom_paint),
            canv.Points(edge_left, point_mode=canv.PointMode.POLYGON, paint=edge_left_paint),
            canv.Points(edge_right, point_mode=canv.PointMode.POLYGON, paint=edge_right_paint),
            *[canv.Points(line, point_mode=canv.PointMode.POLYGON, paint=grid_vlines_paint)
              for line in grid_vlines],
            *[canv.Points(line, point_mode=canv.PointMode.POLYGON, paint=grid_hlines_paint)
              for line in grid_hlines],
        ],
        width=None,  # Будет установлено позже
        height=None,  # Будет установлено позже
        left=0,
        top=0
    )
    
    # Создаем canvas для отображения сетки на левом изображении в режиме просмотра
    mesh_canvas_left = canv.Canvas(
        [
            canv.Points(edge_top, point_mode=canv.PointMode.POLYGON, paint=edge_top_paint),
            canv.Points(edge_bottom, point_mode=canv.PointMode.POLYGON, paint=edge_bottom_paint),
            canv.Points(edge_left, point_mode=canv.PointMode.POLYGON, paint=edge_left_paint),
            canv.Points(edge_right, point_mode=canv.PointMode.POLYGON, paint=edge_right_paint),
            *[canv.Points(line, point_mode=canv.PointMode.POLYGON, paint=grid_vlines_paint)
              for line in grid_vlines],
            *[canv.Points(line, point_mode=canv.PointMode.POLYGON, paint=grid_hlines_paint)
              for line in grid_hlines],
        ],
        width=None,  # Будет установлено позже
        height=None,  # Будет установлено позже
        left=0,
        top=0
    )
    
    return mesh_canvas, mesh_canvas_left

def update_grid_if_needed(state, image_display, page):
    """
    Обновляет сетку при необходимости (добавление новых точек).
    
    Args:
        state: Объект состояния приложения
        image_display: Компонент отображения изображения
        page: Объект страницы
    
    Returns:
        bool: True, если обновление прошло успешно, иначе False
    """
    # Если сетка отображается и чекбокс включен, перестраиваем сетку
    if state.show_grid and state.check_points():
        try:
            # Удаляем старую сетку
            if state.mesh_canvas:
                image_display.remove_mesh_canvas()
            
            # Строим новую сетку
            mesh_canvas, mesh_canvas_left = build_grid(state)
            
            # Устанавливаем размеры canvas
            mesh_canvas.width = image_display.image.width
            mesh_canvas.height = image_display.image.height
            
            # Сохраняем canvas в состояние
            state.mesh_canvas = mesh_canvas
            
            # Показываем новую сетку
            image_display.add_mesh_canvas(mesh_canvas)
            
            return True
        
        except Exception as e:
            state.grid_built = False
            state.show_grid = False
            page.update()
            return False
    
    return False

def handle_grid_toggle(e, state, image_display, page):
    """
    Обработчик переключения отображения сетки.
    
    Args:
        e: Событие переключения
        state: Объект состояния приложения
        image_display: Компонент отображения изображения
        page: Объект страницы
    """
    # Сохраняем текущее состояние чекбокса
    state.show_grid = e.control.value
    
    # Если чекбокс включен, проверяем наличие сетки и строим её при необходимости
    if state.show_grid:
        # Проверяем, достаточно ли точек
        if not state.check_points():
            # Это не должно произойти, так как чекбокс должен быть недоступен в этом случае
            e.control.value = False
            state.show_grid = False
            page.update()
            return
            
        try:
            # Удаляем старую сетку, если она есть
            if state.mesh_canvas:
                image_display.remove_mesh_canvas()
            
            # Строим новую сетку
            mesh_canvas, mesh_canvas_left = build_grid(state)
            
            # Устанавливаем размеры canvas
            mesh_canvas.width = image_display.image.width
            mesh_canvas.height = image_display.image.height
            
            # Сохраняем canvas в состояние
            state.mesh_canvas = mesh_canvas
            
            # Устанавливаем флаг успешного построения сетки
            state.grid_built = True
            
            # Показываем новую сетку
            image_display.add_mesh_canvas(mesh_canvas)
            
        except Exception as e:
            state.grid_built = False
            state.show_grid = False
            e.control.value = False
    else:
        # Если чекбокс выключен, скрываем сетку
        if state.mesh_canvas:
            image_display.remove_mesh_canvas()
    
    # Обновляем UI
    page.update()
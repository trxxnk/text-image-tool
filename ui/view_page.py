import flet as ft
from .components.file_pickers import FilePickerManager
from .handlers.picker_handlers import create_save_image_handler
from .state.app_state import AppState
import cv2
from core.grid_utils import (
    create_coordinate_grid, normalize_grid_coordinates, compute_remap_maps, 
    apply_remap, visualize_grid, visualize_boundary_points,
    preprocess_edges, build_fast_mesh_function, CvColors
)
import numpy as np
import os
import time

def create_loading_overlay():
    """Creates a loading animation overlay for image stacks."""
    return ft.Stack([
        ft.Container(
            bgcolor=ft.colors.with_opacity(0.7, ft.colors.BLACK),
            border_radius=5,
            expand=True
        ),
        ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=4),
                ft.Text("Обработка...", color=ft.colors.WHITE)
            ], 
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.alignment.center
        )
    ])

def process_on_tab_change(page:ft.Page, image_stack_left:ft.Stack,
                          image_stack_right:ft.Stack, state:AppState):
    image_stack_left.controls[0].src = state.current_image_path
    image_stack_right.controls[0].src = state.current_image_path
    
    loading_overlay_left = create_loading_overlay()
    loading_overlay_right = create_loading_overlay()
    
    image_stack_left.controls.append(loading_overlay_left)
    image_stack_right.controls.append(loading_overlay_right)
    
    page.update()
    
    image = cv2.imread(state.current_image_path)
    script_dir = os.path.dirname(os.path.dirname(__file__))
    output_image_path = os.path.join(script_dir, "storage", "output_image.png")
    visualization_path = os.path.join(script_dir, "storage", "visualization.png")
    
    height, width = image.shape[:2]
    grid = create_coordinate_grid(height, width)

    normalized_grid = normalize_grid_coordinates(grid, width, height)
    
    prep_edge_top, prep_edge_bottom, prep_edge_left, prep_edge_right = preprocess_edges(**state.edge_points_lists)
    mesh_func = build_fast_mesh_function(prep_edge_top, prep_edge_bottom, prep_edge_left, prep_edge_right)

    visualization = visualize_grid(
        image, 
        mesh_func, 
        n_points=10, 
        color_horizontal=CvColors.RED, 
        color_vertical=CvColors.BLUE
    )

    edge_points = [prep_edge_top, prep_edge_bottom, prep_edge_left, prep_edge_right]
    colors = [CvColors.RED, CvColors.BLUE, CvColors.GREEN, CvColors.ORANGE]
    visualization = visualize_boundary_points(visualization, edge_points, colors)
    
    cv2.imwrite(visualization_path, visualization)
    image_stack_left.controls[0].src = visualization_path
    page.update()
    if len(image_stack_left.controls) > 1:
        image_stack_left.controls.pop()
    page.update()
    
    map_x, map_y = compute_remap_maps(mesh_func, normalized_grid)
    result = apply_remap(image, map_x, map_y)

    cv2.imwrite(output_image_path, result)
    image_stack_right.controls[0].src = output_image_path
    page.update()
    if len(image_stack_right.controls) > 1:
        image_stack_right.controls.pop()
    page.update()

def create_view_page_content(page: ft.Page, image_stack_left:ft.Stack,
                             image_stack_right:ft.Stack, state: AppState):
    """
    Создает содержимое для режима просмотра результата.
    
    Args:
        page: Объект страницы
        image_stack_left: Стек изображения слева
        image_stack_right: Стек изображения справа
        state: Состояние приложения

    Returns:
        Container: Содержимое страницы просмотра
    """
    # Константы
    STACK_IMAGE_HEIGHT = page.height * 0.7
    
    # Создаем менеджер файловых диалогов
    picker_manager = FilePickerManager(page)

    # Создаем обработчик для сохранения изображения
    image_control = None
    if len(image_stack_right.controls) > 0:
        image_control = image_stack_right.controls[0]
    
    save_image_handler = create_save_image_handler(
        picker_manager, page, image_control
    )

    # Создаем кнопку сохранения изображения
    save_image_button = ft.ElevatedButton(
        "Сохранить изображение",
        on_click=save_image_handler
    )

    # Кнопки управления - размещаем в том же месте для консистентности
    controls_row = ft.Row([
        ft.Container(width=page.width * 0.45), # Пустой контейнер для выравнивания
        ft.Row([
            save_image_button,
        ], spacing=10)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    # Основное содержимое - два изображения рядом
    images_row = ft.Row([
        ft.Container(
            content=image_stack_left,
            expand=True,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            padding=5
        ),
        ft.Container(
            content=image_stack_right,
            expand=True,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            padding=5
        )
    ], expand=True)
    
    # Собираем содержимое
    content = ft.Column([
        controls_row,
        images_row
    ], expand=True)

    return content 
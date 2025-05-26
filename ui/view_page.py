import flet as ft
from .components.file_pickers import FilePickerManager
from .handlers.picker_handlers import create_save_image_handler
from .state.app_state import AppState
import cv2
from core.utilsTest import preprocess_edges_from_main, build_fast_mesh_function, CvColors
import numpy as np
import os
import time

def process_on_tab_change(page:ft.Page, image_stack_left:ft.Stack,
                          image_stack_right:ft.Stack, state:AppState):
    if state.current_image_path:
        print(f" >> Начинаем обработку изображения: `{state.current_image_path}`.")
        script_dir = os.path.dirname(os.path.dirname(__file__))
        output_image_path = os.path.join(script_dir, "storage", "output_image.png")
        visualization_path = os.path.join(script_dir, "storage", "visualization.png")
        
        image = cv2.imread(state.current_image_path)
        image_stack_left.controls[0].src = state.current_image_path
        
        # 2. Создаем целевую сетку координат
        height, width = image.shape[:2]
        grid = np.mgrid[height-1:-1:-1, 0:width:1].swapaxes(0, 2).swapaxes(0, 1)

        # 3. Нормализуем координаты сетки для параметров s и t
        normalized_grid = grid.copy().astype(np.float32)
        normalized_grid[..., 1] /= (width-1)  # s координата (горизонтальная)
        normalized_grid[..., 0] /= (height-1)  # t координата (вертикальная)
        
        # 4. Построение функции трансформации
        prep_edge_top, prep_edge_bottom, prep_edge_left, prep_edge_right = preprocess_edges_from_main(**state.edge_points_lists)
        mesh_func = build_fast_mesh_function(prep_edge_top, prep_edge_bottom, prep_edge_left, prep_edge_right)
        
        # 5. Визуализация граничных сплайнов
        print(f" >> Визуализация сетки...")
        visualization = image.copy()

        n_points = 10
        test_params = []

        for s in np.linspace(0,1,n_points):
            test_params.append(
                (s * np.ones(n_points), np.linspace(0,1,n_points), CvColors.RED)
                )
            
        for t in np.linspace(0,1,n_points):
            test_params.append(
                (np.linspace(0,1,n_points), t * np.ones(n_points), CvColors.BLUE)
                )

        def get_log_thickness(h, w):
            size_factor = np.log10(h * w)
            return max(1, int(size_factor))
        cur_thickness = get_log_thickness(height, width)

        for s, t, color in test_params:
            # Преобразуем одномерные массивы в двумерные
            s_2d = s.reshape(1, -1)  # [1, n_points]
            t_2d = t.reshape(1, -1)  # [1, n_points]
            
            # Получаем преобразованные координаты
            res = mesh_func(s_2d, t_2d)
            # Извлекаем x и y координаты из результата
            x = res[..., 0]  # x координаты теперь в первом канале
            y = res[..., 1]  # y координаты теперь во втором канале
            
            # Создаем массив точек для отрисовки
            points = np.array([x.flatten(), y.flatten()]).T
            points = points.reshape((-1,1,2)).astype(np.int32)
            cv2.polylines(visualization, [points], False, color, cur_thickness)

        # Визуализация граничных точек
        circle_cur_radius = int(cur_thickness * 2)
        cur_thickness = circle_cur_radius * 2
        boundary_points = [
            (prep_edge_top, CvColors.RED, cur_thickness),
            (prep_edge_bottom, CvColors.BLUE, cur_thickness),
            (prep_edge_left, CvColors.GREEN, cur_thickness),
            (prep_edge_right, CvColors.ORANGE, cur_thickness)
        ]
        for points, color, thickness in boundary_points:
            for point in points:
                x, y = int(point[0]), int(point[1])
                cv2.circle(visualization, (x, y), circle_cur_radius, color, thickness)

        # Сохраняем визуализацию трансформированных сплайнов
        cv2.imwrite(visualization_path, visualization)
        image_stack_left.controls[0].src = visualization_path
        print(f" >> Визуализация сетки завершена: `{visualization_path}`.")

        # 7. Конвертируем map_x и map_y в правильный формат для cv2.remap
        print(f" >> Вычисляем map_x и map_y для cv2.remap...")
        start_time = time.time()
        res = mesh_func(normalized_grid[...,1], normalized_grid[...,0])
        map_y = res[...,1]
        map_x = res[...,0]
        map_x = map_x.astype(np.float32)
        map_y = map_y.astype(np.float32)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f" >> Вычисление map_x и map_y завершено ({execution_time:.2f} сек.).")

        # 8. Применяем ремапинг с кубической интерполяцией
        print(f" >> Применяем cv2.remap с кубической интерполяцией...")
        start_time = time.time()
        result = cv2.remap(image,
                        map_x,
                        map_y,
                        interpolation=cv2.INTER_CUBIC,
                        borderMode=cv2.BORDER_CONSTANT)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f" >> Применение cv2.remap завершено ({execution_time:.2f} сек.).")

        # 9. Сохраняем результат
        cv2.imwrite(output_image_path, result)
        image_stack_right.controls[0].src = output_image_path
        print(f" >> Результат сохранен в `{output_image_path}`.")

        page.update()
    else:
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
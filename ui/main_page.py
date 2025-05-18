import flet as ft
import numpy as np
import cv2
from .state.app_state import AppState
from .components.image_display import ImageDisplay
from .components.control_panel import ControlPanel
from .handlers.image_handlers import process_new_image, show_alert
from .handlers.grid_handlers import build_grid
from .utils.file_utils import save_points_to_json, load_points_from_json

def create_main_page_content(page: ft.Page, workflow_tabs, mode_selector, 
                         image_stack_left, image_stack_right):
    """
    Создает содержимое для режима редактирования/ввода точек.
    
    Args:
        page: Объект страницы
        workflow_tabs: Вкладки для переключения между режимами
        mode_selector: Селектор режима работы
        image_stack_left: Стек изображения слева для режима просмотра
        image_stack_right: Стек изображения справа для режима просмотра
        
    Returns:
        Container: Содержимое страницы редактирования
    """
    # Инициализируем состояние
    state = AppState()
    
    # Константы
    STACK_IMAGE_HEIGHT = page.height * 0.7
    
    # Изображения для режима просмотра
    image_display_left = ft.Image(
        fit=ft.ImageFit.CONTAIN,
        visible=False,
        height=STACK_IMAGE_HEIGHT
    )
    
    image_display_right = ft.Image(
        fit=ft.ImageFit.CONTAIN,
        visible=False,
        height=STACK_IMAGE_HEIGHT
    )

    # Обновляем стеки с изображениями
    image_stack_left.controls = [image_display_left]
    image_stack_right.controls = [image_display_right]
    
    # Создаем FilePicker'ы для всех операций с файлами
    file_picker = ft.FilePicker()
    save_picker = ft.FilePicker()
    load_picker = ft.FilePicker()
    
    # Добавляем все FilePicker'ы на страницу
    page.overlay.extend([file_picker, save_picker, load_picker])
    
    # Создаем компонент отображения изображения
    image_display = ImageDisplay(
        state=state,
        height=STACK_IMAGE_HEIGHT,
        on_point_added=lambda: (
            control_panel.update_coords_text(), 
            control_panel.update_button_states(), 
            update_grid_if_needed(),
            page.update()
        )
    )
    
    # Функция для обновления сетки при добавлении новой точки
    def update_grid_if_needed():
        # Если сетка отображается и чекбокс включен, перестраиваем сетку
        if state.show_grid and state.check_points():
            try:
                # Удаляем старую сетку
                if state.mesh_canvas:
                    image_display.remove_mesh_canvas(state.mesh_canvas)
                
                # Строим новую сетку
                mesh_canvas, mesh_canvas_left = build_grid(state)
                
                # Устанавливаем размеры canvas
                mesh_canvas.width = image_display.image.width
                mesh_canvas.height = image_display.image.height
                mesh_canvas_left.width = image_display_left.width
                mesh_canvas_left.height = image_display_left.height
                
                # Сохраняем canvas в состояние
                state.mesh_canvas = mesh_canvas
                state.mesh_canvas_left = mesh_canvas_left
                
                # Показываем новую сетку
                image_display.add_mesh_canvas(mesh_canvas)
                
                # Автоматически применяем сетку к режиму просмотра
                handle_apply(None)
            except Exception as e:
                show_alert(page, f"Ошибка при обновлении сетки: {str(e)}")
                state.grid_built = False
                control_panel.show_grid_checkbox.value = False
                state.show_grid = False
                page.update()

    # Обработчики событий
    def handle_file_upload(e: ft.FilePickerResultEvent):
        if e.files and e.files[0].path:
            process_new_image(
                e.files[0].path,
                state,
                image_display,
                image_display_left,
                image_display_right,
                STACK_IMAGE_HEIGHT
            )
            # Сбрасываем флаги и обновляем чекбокс
            state.show_grid = False
            state.grid_built = False
            state.mesh_canvas = None
            state.mesh_canvas_left = None
            control_panel.show_grid_checkbox.value = False
            control_panel.update_coords_text()
            control_panel.update_button_states()
            page.update()
            
    def handle_clear(_):
        # Очищаем точки в состоянии
        state.clear_points()
        
        # Сбрасываем флаги
        state.grid_built = False
        state.show_grid = False
        
        # Удаляем сетку, если она отображается
        if state.mesh_canvas:
            image_display.remove_mesh_canvas(state.mesh_canvas)
            state.mesh_canvas = None
            state.mesh_canvas_left = None
        
        # Очищаем UI
        image_display.clear()
        
        # Обновляем состояние чекбокса
        control_panel.show_grid_checkbox.value = False
        
        # Обновляем UI панели управления
        control_panel.update_coords_text()
        control_panel.update_button_states()
        page.update()
        
    def handle_save(_):
        if not state.current_image_path:
            show_alert(page, "Сначала загрузите изображение!")
            return
            
        def handle_save_result(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    save_points_to_json(state.edge_points_lists, state.current_image_path, e.path)
                    show_alert(page, "Точки успешно сохранены!")
                except Exception as e:
                    show_alert(page, f"Ошибка при сохранении: {str(e)}")
        
        save_picker.on_result = handle_save_result
        save_picker.save_file(
            allowed_extensions=["json"],
            file_name="points.json"
        )
        
    def handle_load(_):
        def handle_load_result(e: ft.FilePickerResultEvent):
            if e.files:
                try:
                    load_data = load_points_from_json(e.files[0].path)
                    
                    # Проверяем наличие необходимых данных
                    for edge_name in state.edge_points_lists.keys():
                        if edge_name not in load_data["points"].keys():
                            show_alert(page, "Некорректный формат файла!")
                            return
                    
                    process_new_image(
                        load_data["image_path"],
                        state,
                        image_display,
                        image_display_left,
                        image_display_right,
                        STACK_IMAGE_HEIGHT
                    )
                    
                    # Загружаем точки
                    for border, points in load_data["points"].items():
                        state.edge_points_lists[border].extend(points)
                        temp_points = np.array(points, dtype=int) / state.ratio
                        state.points_lists[border].extend(temp_points.tolist())
                        
                        # Добавляем точки на изображение
                        point_radius = 4
                        for p in temp_points:
                            point = ft.Container(
                                content=ft.CircleAvatar(
                                    bgcolor=state.colors[border],
                                    radius=point_radius,
                                ),
                                left=(p[0]-point_radius),
                                top=(p[1]-point_radius)
                            )
                            image_display.stack.controls.append(point)
                    
                    # Обновляем состояние
                    control_panel.update_coords_text()
                    control_panel.update_button_states()
                    
                    page.update()
                    
                except Exception as e:
                    show_alert(page, f"Ошибка при загрузке: {str(e)}")
        
        load_picker.on_result = handle_load_result
        load_picker.pick_files(
            allowed_extensions=["json"]
        )
        
    def handle_apply(_):
        # Проверяем наличие сетки или возможность её построения
        if not state.grid_built and not state.check_points():
            show_alert(page, "Необходимо добавить минимум по 2 точки для каждой границы!")
            return
            
        try:
            # Если сетка не построена, но есть достаточно точек - построим её
            if not state.grid_built and state.check_points():
                # Строим новую сетку
                mesh_canvas, mesh_canvas_left = build_grid(state)
                
                # Устанавливаем размеры canvas
                mesh_canvas.width = image_display.image.width
                mesh_canvas.height = image_display.image.height
                mesh_canvas_left.width = image_display_left.width
                mesh_canvas_left.height = image_display_left.height
                
                # Сохраняем canvas в состояние
                state.mesh_canvas = mesh_canvas
                state.mesh_canvas_left = mesh_canvas_left
                
                # Устанавливаем флаг успешного построения сетки
                state.grid_built = True
                
            # Обновляем изображения в режиме просмотра
            # Добавляем сетку на левое изображение в режиме просмотра
            image_stack_left.controls = [image_display_left]
            
            # Добавляем mesh_canvas_left если он существует
            if state.mesh_canvas_left:
                # Убедимся, что размеры canvas соответствуют изображению
                state.mesh_canvas_left.width = image_display_left.width
                state.mesh_canvas_left.height = image_display_left.height
                image_stack_left.controls.append(state.mesh_canvas_left)
                
            # Добавляем точки поверх сетки для левого изображения
            point_radius = 4
            for border, points in state.points_lists.items():
                for p in points:
                    # Масштабируем точки относительно размера изображения в режиме просмотра
                    scaled_x = p[0] * (image_display_left.width / image_display.image.width)
                    scaled_y = p[1] * (image_display_left.height / image_display.image.height)
                    
                    new_point = ft.Container(
                        content=ft.CircleAvatar(
                            bgcolor=state.colors[border],
                            radius=point_radius,
                        ),
                        left=(scaled_x-point_radius),
                        top=(scaled_y-point_radius),
                    )
                    image_stack_left.controls.append(new_point)
            
            # Переключаемся на вкладку просмотра
            workflow_tabs.selected_index = 1
            workflow_tabs.on_change(ft.ControlEvent(workflow_tabs, "selected_index"))
                
            page.update()
            
        except Exception as e:
            show_alert(page, f"Ошибка при применении сетки: {str(e)}")
        
    def handle_grid_toggle(e):
        # Сохраняем текущее состояние чекбокса
        state.show_grid = e.control.value
        
        # Если чекбокс включен, проверяем наличие сетки и строим её при необходимости
        if state.show_grid:
            # Проверяем, достаточно ли точек
            if not state.check_points():
                # Это не должно произойти, так как чекбокс должен быть недоступен в этом случае
                show_alert(page, "Необходимо добавить минимум по 2 точки для каждой границы!")
                e.control.value = False
                state.show_grid = False
                page.update()
                return
                
            try:
                # Строим новую сетку, если её ещё нет или нужно обновить
                # Удаляем старую сетку, если она есть
                if state.mesh_canvas:
                    image_display.remove_mesh_canvas(state.mesh_canvas)
                
                # Строим новую сетку
                mesh_canvas, mesh_canvas_left = build_grid(state)
                
                # Устанавливаем размеры canvas
                mesh_canvas.width = image_display.image.width
                mesh_canvas.height = image_display.image.height
                mesh_canvas_left.width = image_display_left.width
                mesh_canvas_left.height = image_display_left.height
                
                # Сохраняем canvas в состояние
                state.mesh_canvas = mesh_canvas
                state.mesh_canvas_left = mesh_canvas_left
                
                # Устанавливаем флаг успешного построения сетки
                state.grid_built = True
                
                # Показываем новую сетку
                image_display.add_mesh_canvas(mesh_canvas)
                
                # Автоматически применяем сетку к режиму просмотра
                handle_apply(None)
                
            except Exception as e:
                show_alert(page, f"Ошибка при построении сетки: {str(e)}")
                state.grid_built = False
                state.show_grid = False
                e.control.value = False
        else:
            # Если чекбокс выключен, скрываем сетку
            if state.mesh_canvas:
                image_display.remove_mesh_canvas(state.mesh_canvas)
        
        # Обновляем UI
        page.update()
            
    # Настраиваем FilePicker для загрузки изображений
    file_picker.on_result = handle_file_upload
    
    # Создаем панель управления
    control_panel = ControlPanel(
        state=state,
        on_upload=lambda _: file_picker.pick_files(
            allowed_extensions=["png", "jpg", "jpeg", "bmp", "gif"]
        ),
        on_clear=handle_clear,
        on_save=handle_save,
        on_load=handle_load,
        on_grid_toggle=handle_grid_toggle
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
    
    # Здесь добавляем обработчик загрузки страницы
    def on_page_load(_):
        control_panel.update_button_states()
        page.update()
    
    page.on_load = on_page_load

    return content
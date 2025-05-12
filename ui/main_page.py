import flet as ft
import numpy as np
import cv2
from .state.app_state import AppState
from .components.image_display import ImageDisplay
from .components.control_panel import ControlPanel
from .handlers.image_handlers import process_new_image, show_alert
from .handlers.grid_handlers import build_grid
from .utils.file_utils import save_points_to_json, load_points_from_json

def create_main_page(page: ft.Page):
    # Инициализируем состояние
    state = AppState()
    
    # Константы
    STACK_IMAGE_HEIGHT = page.height * 0.7
    
    # Заглушки для обработчиков, которые будут определены позже
    def handle_clear(_): pass
    def handle_build_grid(_): pass
    def handle_apply(_): pass
    def handle_save(_): pass
    def handle_load(_): pass
    def handle_grid_toggle(_): pass
    
    # Создаем панель управления до создания ImageDisplay
    control_panel = ControlPanel(
        state=state,
        on_upload=lambda _: file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg", "tif", "tiff"]
        ),
        on_clear=handle_clear,
        on_build_grid=handle_build_grid,
        on_apply=handle_apply,
        on_save=handle_save,
        on_load=handle_load,
        on_grid_toggle=handle_grid_toggle
    )
    
    # Теперь создаем компонент отображения изображения с callback'ом
    image_display = ImageDisplay(
        state=state,
        height=STACK_IMAGE_HEIGHT,
        on_point_added=lambda: (control_panel.update_coords_text(), control_panel.update_button_states(), page.update())
    )
    
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

    # Stack для изображений в режиме просмотра
    image_stack_left = ft.Stack(
        [image_display_left],
    )
    
    image_stack_right = ft.Stack(
        [image_display_right],
    )
    
    # Создаем FilePicker'ы для всех операций с файлами
    file_picker = ft.FilePicker()
    save_picker = ft.FilePicker()
    load_picker = ft.FilePicker()
    
    # Добавляем все FilePicker'ы на страницу
    page.overlay.extend([file_picker, save_picker, load_picker])
    
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
            # Флаги уже сбрасываются в process_new_image, но нужно обновить чекбокс в UI
            control_panel.show_grid_checkbox.value = False
            control_panel.update_coords_text()
            control_panel.update_button_states()
            page.update()
            
    def handle_clear(_):
        # Очищаем точки в состоянии
        state.clear_points()
        
        # Сбрасываем флаги, как при загрузке нового изображения
        state.grid_built = False
        state.show_grid = False
        
        # Удаляем сетку, если она отображается
        if state.mesh_canvas:
            image_display.remove_mesh_canvas(state.mesh_canvas)
        
        # Очищаем UI
        image_display.clear()
        
        # Обновляем состояние чекбокса
        control_panel.show_grid_checkbox.value = False
        
        # Обновляем UI панели управления
        control_panel.update_coords_text()
        control_panel.update_button_states()
        page.update()
        
    def handle_build_grid(_):
        if not state.check_points():
            show_alert(page, "Необходимо добавить минимум по 2 точки для каждой границы!")
            return
            
        try:
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
            
            # Обновляем состояние компонентов
            control_panel.update_button_states()
            
            # Если чекбокс включен, показываем новую сетку
            if state.show_grid:
                image_display.add_mesh_canvas(mesh_canvas)
                
            page.update()
            
        except Exception as e:
            show_alert(page, f"Ошибка при построении сетки: {str(e)}")
            state.grid_built = False
            control_panel.update_button_states()
            
    def handle_grid_toggle(e):
        state.show_grid = e.control.value
        if state.show_grid:
            image_display.add_mesh_canvas(state.mesh_canvas)
        else:
            image_display.remove_mesh_canvas(state.mesh_canvas)
            
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
        # Обновляем изображения в режиме просмотра
        if state.grid_built:
            # Добавляем сетку на левое изображение в режиме просмотра
            image_stack_left.controls = [image_display_left, state.mesh_canvas_left]
            
            # Добавляем точки поверх сетки для левого изображения
            point_radius = 4
            for border, points in state.points_lists.items():
                for p in points:
                    new_point = ft.Container(
                        content=ft.CircleAvatar(
                            bgcolor=state.colors[border],
                            radius=point_radius,
                        ),
                        left=(p[0]-point_radius),
                        top=(p[1]-point_radius),
                    )
                    image_stack_left.controls.append(new_point)
            
        # Переключаемся на режим просмотра
        page.go("/view")
        
    # Настраиваем FilePicker для загрузки изображений
    file_picker.on_result = handle_file_upload
    
    # Создаем панель управления
    control_panel = ControlPanel(
        state=state,
        on_upload=lambda _: file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg", "tif", "tiff"]
        ),
        on_clear=handle_clear,
        on_build_grid=handle_build_grid,
        on_apply=handle_apply,
        on_save=handle_save,
        on_load=handle_load,
        on_grid_toggle=handle_grid_toggle
    )

    # Макет 1 (основной режим)
    layout1 = ft.Row([
        ft.Container(
            content=image_display.container,
            width=page.width * 0.5,
            height=STACK_IMAGE_HEIGHT,
            alignment=ft.alignment.center
        ),
        ft.Container(
            content=control_panel.content,
        )
    ], spacing=20)
    
    # Здесь добавляем обработчик загрузки страницы
    def on_page_load(_):
        control_panel.update_button_states()
        page.update()
    
    page.on_load = on_page_load

    return layout1, image_stack_left, image_stack_right
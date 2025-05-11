import flet as ft
from flet import canvas as canv
import cv2
import tempfile
import numpy as np
from core.utils import build_mesh_function, preprocess_edges

def create_main_page(page: ft.Page):
    # Названия границ
    border_names = ["edge_top", "edge_bottom", "edge_left", "edge_right"]

    # Списки для хранения точек разных границ
    points_lists = {name: [] for name in border_names}
    
    # Цвета для границ
    colors = {
        "edge_top": ft.Colors.RED,
        "edge_bottom": ft.Colors.BLUE,
        "edge_left": ft.Colors.GREEN,
        "edge_right": ft.Colors.ORANGE
    }
    # Текущая выбранная граница
    current_border = "edge_top"

    # Флаг для отслеживания успешного построения сетки
    grid_built = False
    # Флаг для отображения сетки
    show_grid = False

    # Путь к текущему изображению
    current_image_path = None

    # Изображения для обоих режимов
    image_display = ft.Image(
        fit=ft.ImageFit.CONTAIN,
        visible=False,
        height=page.height * 0.7,
    )
    
    # Stack для наложения точек на изображение
    image_stack = ft.Stack(
        [image_display],
    )

    # Функция для обработки клика по изображению
    def handle_image_click(e: ft.TapEvent):
        if image_display.visible:
            # Получаем координаты клика относительно изображения
            x = e.local_x
            y = e.local_y
            
            # Создаем точку
            point = ft.Container(
                content=ft.CircleAvatar(
                    bgcolor=colors[current_border],
                    radius=5,
                ),
                left = x - 5,  # Центрируем точку относительно клика
                top = y - 5
            )
            
            points_lists[current_border].append((x, y))
            image_stack.controls.append(point)
            
            update_coords_text()
            update_button_states()
            page.update()

    # GestureDetector для отслеживания кликов
    gesture = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.CLICK,
        content=image_stack,
        on_tap_up=handle_image_click
    )

    # Для правой панели: отдельный список для отображения точек после построения сетки
    built_points = {name: [] for name in border_names}

    # Изображение для режима просмотра (Layout 2)
    image_display_left = ft.Image(
        fit=ft.ImageFit.CONTAIN,
        visible=False,
        height=page.height * 0.7
    )
    
    image_display_right = ft.Image(
        fit=ft.ImageFit.CONTAIN,
        visible=False,
        height=page.height * 0.7
    )

    # Stack для изображений в режиме просмотра
    image_stack_left = ft.Stack(
        [image_display_left],
    )
    
    image_stack_right = ft.Stack(
        [image_display_right],
    )

    # Переменная для хранения сетки (canvas)
    mesh_canvas = None
    mesh_canvas_left = None

    # Функция для добавления водяного знака на изображение
    def add_watermark(image_path):
        # Загружаем изображение
        img = cv2.imread(image_path)
        if img is None:
            show_alert("Ошибка при загрузке изображения для водяного знака")
            return None
            
        # Размер изображения
        h, w, _ = img.shape
        
        # Создаем overlay с текстом
        overlay = img.copy()
        
        # Настройки текста
        text = "CHANGED IMAGE"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = w / 500  # Масштабируем размер шрифта в зависимости от ширины изображения
        thickness = max(1, int(w / 500))  # Толщина шрифта
        
        # Получаем размер текста
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        
        # Рассчитываем позицию (центр изображения)
        text_x = (w - text_size[0]) // 2
        text_y = (h + text_size[1]) // 2
        
        # Добавляем текст на overlay
        cv2.putText(overlay, text, (text_x, text_y), font, font_scale, (0, 0, 255), thickness)
        
        # Наложение с прозрачностью (alpha blending)
        alpha = 1  # Прозрачность: 0.0 (прозрачный) - 1.0 (непрозрачный)
        result = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
        
        # Сохраняем результат во временный файл
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        cv2.imwrite(temp_file.name, result)
        
        return temp_file.name

    # Создаем диалог для предупреждений
    def show_alert(message):
        def on_click(_):
            page.dialog.open = False
        dlg = ft.AlertDialog(
            title=ft.Text("Предупреждение"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=on_click)
            ]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # Функция для обработки загрузки файла
    def handle_file_upload(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            if file_path:
                # Сохраняем путь к текущему изображению
                nonlocal current_image_path
                current_image_path = file_path
                
                # Сбрасываем флаг построения сетки
                nonlocal grid_built, show_grid
                grid_built = False
                show_grid = False
                show_grid_checkbox.value = False
                
                for border in points_lists:
                    points_lists[border].clear()
                    built_points[border].clear()
                
                # Обновляем изображения для обоих режимов
                image_stack.controls = [image_display]
                image_display.src = file_path
                image_display.visible = True
                
                image_stack_left.controls = [image_display_left]
                image_display_left.src = file_path
                image_display_left.visible = True
                
                # Создаем версию изображения с водяным знаком для правой панели
                watermarked_image = add_watermark(file_path)
                if watermarked_image:
                    image_display_right.src = watermarked_image
                else:
                    image_display_right.src = file_path
                
                image_display_right.visible = True
                
                # Настраиваем размеры стеков в соответствии с изображением
                image_stack.width = image_display.width
                image_stack.height = image_display.height
                image_stack_left.width = image_display_left.width 
                image_stack_left.height = image_display_left.height
                image_stack_right.width = image_display_right.width
                image_stack_right.height = image_display_right.height
                
                update_coords_text()
                update_button_states()
                page.update()

    # Создаем FilePicker
    file_picker = ft.FilePicker(on_result=handle_file_upload)
    page.overlay.append(file_picker)

    # Создаем кнопку загрузки
    upload_button = ft.ElevatedButton(
        "Загрузить изображение",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg", "tif", "tiff"]
        )
    )

    # Создаем текстовое поле для отображения координат
    coords_text = ft.Text(size=16)

    # Обновление текста с координатами
    def update_coords_text():
        for border, points in points_lists.items():
            if points:
                coords = ", ".join("({:.0f} , {:.0f})".format(*p) for p in points)
                coords_texts[border].value = f"{border}: {coords}"
            else:
                coords_texts[border].value = f"{border}: нет точек"
        page.update()

    # Создаем текстовые поля для каждой границы
    coords_texts = {
        name: ft.Text(f"{name}: ", size=16, color=colors[name]) 
        for name in border_names
    }

    # Кнопка для очистки точек
    def clear_points(e):
        nonlocal grid_built, show_grid
        grid_built = False
        show_grid = False
        show_grid_checkbox.value = False
        
        for border in points_lists:
            points_lists[border].clear()
        image_stack.controls = [image_display]
        update_coords_text()
        update_button_states()
        page.update()

    clear_button = ft.ElevatedButton(
        "Очистить точки", 
        on_click=clear_points,
        icon=ft.icons.DELETE,
    )

    # Обработчик изменения границы для Dropdown
    def border_changed(e):
        nonlocal current_border
        current_border = e.control.value
        page.update()

    # Выпадающее меню для выбора границы
    border_selector = ft.Dropdown(
        options=[
            ft.dropdown.Option(key=name, text=name) for name in border_names
        ],
        value=current_border,
        on_change=border_changed,
        width=200
    )
    
    # Функция проверки наличия достаточного числа точек
    def check_points():
        for border, points in points_lists.items():
            if len(points) < 2:
                return False
        return True

    # Функция для обработки изменения состояния показа сетки
    def toggle_grid(e):
        nonlocal show_grid
        show_grid = e.control.value
        update_grid_display()
        page.update()
    
    # Checkbox для отображения сетки
    show_grid_checkbox = ft.Checkbox(
        label="Показать сетку",
        value=False,
        on_change=toggle_grid,
        disabled=True  # Изначально неактивен
    )
    
    # Обновление отображения сетки
    def update_grid_display():
        if not grid_built or mesh_canvas is None:
            return
            
        # Если сетка построена и флаг включен, добавляем canvas на исходное изображение
        if show_grid:
            # Проверяем, есть ли уже canvas в image_stack
            if mesh_canvas not in image_stack.controls:
                # Помещаем canvas между исходным изображением и точками
                controls = [image_display, mesh_canvas]
                # Добавляем все точки, которые уже были на изображении
                for control in image_stack.controls[1:]:
                    controls.append(control)
                image_stack.controls = controls
        else:
            # Если флаг выключен, удаляем canvas из image_stack
            if mesh_canvas in image_stack.controls:
                image_stack.controls.remove(mesh_canvas)
        
        page.update()

    # Кнопка "Построить криволинейную сетку"
    def build_grid(e):
        # Проверяем наличие точек
        if not check_points():
            show_alert("Необходимо добавить минимум по 2 точки для каждой границы!")
            return
            
        nonlocal grid_built, mesh_canvas, mesh_canvas_left
        
        # Очищаем старые точки
        for border in built_points:
            built_points[border].clear()
            
        image_stack_right.controls = [image_display_right]
        
        # Строим функцию криволинейной сетки    
        try:
            edge_top, edge_bottom, edge_left, edge_right = preprocess_edges(**points_lists)
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
                width=image_display.width,
                height=image_display.height,
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
                width=image_display_left.width,
                height=image_display_left.height,
                left=0,
                top=0
            )
            
            # Установим флаг успешного построения сетки
            grid_built = True
            
            # Разблокируем чекбокс и обновим состояние кнопок
            show_grid_checkbox.disabled = False
            update_button_states()
            
            # Если чекбокс уже включен, обновляем отображение сетки
            if show_grid:
                update_grid_display()
                
            page.update()
            
        except Exception as e:
            show_alert(f"Ошибка при построении сетки: {str(e)}")
            grid_built = False
            show_grid_checkbox.disabled = True
            update_button_states()

    build_button = ft.ElevatedButton(
        "Построить сетку",
        icon=ft.icons.GRID_4X4,
        on_click=build_grid,
        disabled=True  # Изначально неактивна
    )

    # Функция для переключения в режим просмотра
    def switch_to_view_mode(e):
        # Обновляем изображения в режиме просмотра
        if grid_built:
            # Добавляем сетку на левое изображение в режиме просмотра
            image_stack_left.controls = [image_display_left, mesh_canvas_left]
            
            # Добавляем точки поверх сетки для левого изображения
            for border, points in points_lists.items():
                for p in points:
                    new_point = ft.Container(
                        content=ft.CircleAvatar(
                            bgcolor=colors[border],
                            radius=5,
                        ),
                        left=p[0] - 5,
                        top=p[1] - 5,
                    )
                    image_stack_left.controls.append(new_point)
            
        # Переключаемся на режим просмотра
        page.go("/view")

    apply_button = ft.ElevatedButton(
        "Применить",
        icon=ft.icons.CHECK,
        on_click=switch_to_view_mode,
        disabled=True  # Изначально неактивна
    )
    
    # Функция обновления состояния кнопок
    def update_button_states():
        # Кнопка построения сетки активна только если есть достаточно точек
        build_button.disabled = not check_points()
        
        # Кнопка применения активна только после успешного построения сетки
        apply_button.disabled = not grid_built
        
        page.update()

    # Компонент с текущими координатами
    coords_container = ft.Container(
        content=ft.Column([
            coords_texts[name] for name in border_names
        ], spacing=5),
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=5,
        expand=True
    )

    # Панель управления (правая часть Layout 1)
    control_panel = ft.Column([
        ft.Text("Управление", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Выберите границу:", size=16),
        border_selector,
        ft.Row([
            upload_button,
            clear_button
        ], spacing=10, wrap=True),
        ft.Row([
            build_button,
            apply_button
        ], spacing=10, wrap=True),
        show_grid_checkbox,
        ft.Text("Координаты точек:", size=16),
        coords_container
    ], spacing=20, expand=True)
    
    # Макет 1 (основной режим)
    layout1 = ft.Row([
        ft.Container(
            content=gesture,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            padding=5,
            width=page.width * 0.5,
            height=page.height * 0.7,
            alignment=ft.alignment.center
        ),
        ft.Container(
            content=control_panel,
        )
    ], spacing=20)

    return layout1, image_stack_left, image_stack_right 
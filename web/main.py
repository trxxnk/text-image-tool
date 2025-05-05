import flet as ft
import os

def main(page: ft.Page):
    # Настройка страницы
    page.adaptive = True
    page.title = "Ввод граничных точек"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # Названия границ
    border_names = ["Верхняя", "Нижняя", "Левая", "Правая"]

    # Списки для хранения точек разных границ
    points_lists = {name: [] for name in border_names}

    # Цвета для границ
    colors = {
        "Верхняя": ft.Colors.RED,
        "Нижняя": ft.Colors.BLUE,
        "Левая": ft.Colors.GREEN,
        "Правая": ft.Colors.ORANGE
    }

    # Текущая выбранная граница
    current_border = "Верхняя"

    # Создаем область для отображения изображения
    image_display = ft.Image(
        fit=ft.ImageFit.CONTAIN,
        visible=False
    )
    
    # Создаем Stack для наложения точек на изображение
    image_stack = ft.Stack(
        [
            image_display,
        ],
        width=image_display.width,
        height=image_display.height
    )

    # Для правой панели: отдельный список для отображения точек после построения сетки
    built_points = {name: [] for name in border_names}

    # Дубликат изображения для правой панели
    image_display_right = ft.Image(
        fit=ft.ImageFit.CONTAIN,
        visible=False
    )

    # Stack для правой панели
    image_stack_right = ft.Stack(
        [
            image_display_right,
        ],
        width=None,
        height=None
    )

    # Функция для обновления размеров изображений и стэков
    def update_image_size(e=None):
        window_width = page.width
        window_height = page.height
        img_w = int(window_width * 0.3)
        img_h = int(window_height * 0.5)
        for img, stack in [
            (image_display, image_stack),
            (image_display_right, image_stack_right)
        ]:
            img.width = img_w
            img.height = img_h
            stack.width = img_w
            stack.height = img_h
        page.update()

    page.on_resize = update_image_size

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
                top = y - 5,
            )
            
            # Добавляем точку в соответствующий список и на изображение
            points_lists[current_border].append(point)
            image_stack.controls.append(point)
            page.update()
            
            update_coords_text()
            page.update()

    # GestureDetector для отслеживания кликов
    gesture = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.CLICK,
        content=image_stack,
        on_tap_up=handle_image_click
    )

    # Функция для обработки загрузки файла
    def handle_file_upload(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            if file_path:
                for border in points_lists:
                    points_lists[border].clear()
                    built_points[border].clear()
                image_stack.controls = [image_display]
                image_stack_right.controls = [image_display_right]
                image_display.src = file_path
                image_display.visible = True
                image_display_right.src = file_path
                image_display_right.visible = True
                update_image_size()
                update_coords_text()
                page.update()

    # Создаем FilePicker
    file_picker = ft.FilePicker(
        on_result=handle_file_upload
    )
    page.overlay.append(file_picker)

    # Создаем кнопку загрузки
    upload_button = ft.ElevatedButton(
        "Загрузить изображение",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg", "tif", "tiff"]
        )
    )

    # Создаем текстовые поля для каждой границы
    coords_texts = {
        name: ft.Text(f"{name}: ", size=16, color=colors[name]) 
        for name in border_names
    }

    # Обновление текста с координатами
    def update_coords_text():
        for border, points in points_lists.items():
            if points:
                coords = ", ".join(f"({p.left + 5:.0f},{p.top + 5:.0f})" for p in points)
                coords_texts[border].value = f"{border}: {coords}"
            else:
                coords_texts[border].value = f"{border}: нет точек"
        page.update()

    # Кнопка для очистки точек
    def clear_points(e):
        for border in points_lists:
            points_lists[border].clear()
        image_stack.controls = [image_display]
        page.update()
        update_coords_text()

    clear_button = ft.ElevatedButton(
        "Очистить точки", 
        on_click=clear_points,
        icon=ft.Icons.DELETE,
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
        width=150
    )

    # Блок выбора границы и кнопок
    border_and_buttons_row = ft.Row(
        [
            ft.Column([
                ft.Text("Текущая граница:", size=16),
                border_selector
            ], spacing=5),
            ft.Column(
                [
                    upload_button,
                    clear_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

    # Кнопка "Построить криволинейную сетку"
    def build_grid(e):
        # Очищаем старые точки
        for border in built_points:
            built_points[border].clear()
        image_stack_right.controls = [image_display_right]
        # Копируем точки из левой панели
        for border, points in points_lists.items():
            for p in points:
                # Копируем координаты и цвет
                new_point = ft.Container(
                    content=ft.CircleAvatar(
                        bgcolor=colors[border],
                        radius=5,
                    ),
                    left=p.left,
                    top=p.top,
                )
                built_points[border].append(new_point)
                image_stack_right.controls.append(new_point)
        page.update()

    build_button = ft.ElevatedButton(
        "Построить криволинейную сетку",
        icon=ft.Icons.GRID_4X4,
        on_click=build_grid
    )

    # Левая панель
    left_panel = ft.Column(
        [
            ft.Text("Ввод граничных точек", size=30, weight=ft.FontWeight.BOLD),
            # Блок выбора границы и кнопок
            border_and_buttons_row,
            gesture,
            ft.Container(
                content=ft.Column([
                    coords_texts[name] for name in border_names
                ], spacing=5),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
        spacing=15
    )

    # Правая панель
    right_panel = ft.Column(
        [
            ft.Text("Криволинейная сетка", size=30, weight=ft.FontWeight.BOLD),
            build_button,
            image_stack_right
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
        spacing=15
    )

    # Основной layout
    page.add(
        ft.Row(
            [
                ft.Container(left_panel, expand=True, padding=10),
                ft.Container(right_panel, expand=True, padding=10)
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START
        )
    )

    # Устанавливаем начальные размеры
    update_image_size()


if __name__ == "__main__":
    ft.app(target=main)

import flet as ft
import os

def main(page: ft.Page):
    # Настройка страницы
    page.title = "Загрузка изображения"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # Списки для хранения точек разных цветов
    points_lists = {
        "Красный": [],
        "Синий": [],
        "Зеленый": [],
        "Желтый": []
    }
    
    # Цвета для точек
    colors = {
        "Красный": ft.Colors.RED,
        "Синий": ft.Colors.BLUE,
        "Зеленый": ft.Colors.GREEN,
        "Желтый": ft.Colors.YELLOW
    }
    
    # Текущий выбранный цвет
    current_color = "Красный"

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

    # Функция для обновления размеров изображения
    def update_image_size(e=None):
        window_width = page.width
        window_height = page.height
        image_display.width = int(window_width * 0.7)
        image_display.height = int(window_height * 0.7)
        image_stack.width = image_display.width
        image_stack.height = image_display.height
        page.update()

    # Подписываемся на изменение размера окна
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
                    bgcolor=colors[current_color],
                    radius=5,
                ),
                left = x - 5,  # Центрируем точку относительно клика
                top = y - 5,
            )
            
            # Добавляем точку в соответствующий список и на изображение
            points_lists[current_color].append(point)
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
                # Очищаем все точки
                for color in points_lists:
                    points_lists[color].clear()
                image_stack.controls = [image_display]
                
                # Обновляем изображение
                image_display.src = file_path
                image_display.visible = True
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

    # Создаем текстовые поля для каждого цвета
    coords_texts = {
        color: ft.Text(f"{color}: ", size=16, color=colors[color]) 
        for color in colors.keys()
    }

    # Обновление текста с координатами
    def update_coords_text():
        for color, points in points_lists.items():
            if points:
                coords = ", ".join(f"({p.left + 5:.0f},{p.top + 5:.0f})" for p in points)
                coords_texts[color].value = f"{color}: {coords}"
            else:
                coords_texts[color].value = f"{color}: нет точек"
        page.update()

    # Создаем переключатель цветов
    def color_changed(e):
        nonlocal current_color
        current_color = e.control.value
        page.update()

    color_selector = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value=color, label=color) for color in colors.keys()
        ], alignment=ft.MainAxisAlignment.CENTER),
        value=current_color,
        on_change=color_changed
    )

    # Кнопка для очистки точек
    def clear_points(e):
        for color in points_lists:
            points_lists[color].clear()
        image_stack.controls = [image_display]
        page.update()
        update_coords_text()

    clear_button = ft.ElevatedButton(
        "Очистить точки", 
        on_click=clear_points,
        icon=ft.Icons.DELETE,
    )

    # Добавляем элементы на страницу
    page.add(
        ft.Column(
            [
                ft.Text("Загрузка изображения", size=30, weight=ft.FontWeight.BOLD),
                upload_button,
                ft.Container(
                    content=ft.Column([
                        ft.Text("Выберите цвет точек:", size=16),
                        color_selector
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center
                ),
                gesture,
                clear_button,
                ft.Container(
                    content=ft.Column([
                        coords_texts[color] for color in colors.keys()
                    ], spacing=5),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=5
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    # Устанавливаем начальные размеры
    update_image_size()

ft.app(target=main)

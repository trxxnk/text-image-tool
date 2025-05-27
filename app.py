import flet as ft
from ui.main_page import create_main_page_content
from ui.view_page import create_view_page_content, process_on_tab_change
from ui.auto_page import create_auto_page_content
from ui.state.app_state import AppState

def main(page: ft.Page):
    # Настройка страницы
    page.title = "Обработка изображений"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # Константы
    STACK_IMAGE_HEIGHT = page.height * 0.7

    # Создаем общие компоненты для обоих режимов
    image_stack_left = ft.Stack([ft.Image()], height=STACK_IMAGE_HEIGHT)
    image_stack_right = ft.Stack([ft.Image()], height=STACK_IMAGE_HEIGHT)
    
    # Инициализируем состояние
    state = AppState()
    
    # Создаем контейнеры для содержимого режимов
    input_container = ft.Container(expand=True)
    view_container = ft.Container(expand=True, visible=False)
    auto_container = ft.Container(expand=True, visible=False)
    
    # Функция переключения между режимами рабочего процесса
    def switch_workflow_mode(e):
        selected_index = e.control.selected_index
        if selected_index == 0:  # Выбран режим "Ввод границ"
            input_container.visible = True
            view_container.visible = False

        else:  # Выбран режим "Выравнивание"
            if not state.current_image_path:
                e.control.selected_index = 0
                dialog = ft.AlertDialog(
                    title=ft.Text("Загрузите изображение"),
                    content=ft.Text("Для применения трансформации необходимо загрузить изображение."),
                    actions=[
                        ft.TextButton("OK", on_click=lambda _: page.close(dialog))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END
                )
                page.open(dialog)
                page.update()
                return
            
            if not state.check_points():
                e.control.selected_index = 0
                dialog = ft.AlertDialog(
                    title=ft.Text("Недостаточно точек"),
                    content=ft.Text("Для применения трансформации необходимо отметить\n"
                                    "минимум по 2 точки для каждой границы."),
                    actions=[
                        ft.TextButton("OK", on_click=lambda _: page.close(dialog))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END
                )
                page.open(dialog)
                page.update()
                return
    
            input_container.visible = False
            view_container.visible = True
            process_on_tab_change(page, image_stack_left, image_stack_right, state) # TODO
        
        # Форсируем обновление UI
        page.update()
    
    # Функция переключения между ручным и авто режимами
    def switch_hand_auto_mode(e):
        selected_index = e.control.selected_index
        # Показываем или скрываем авто-режим
        if selected_index == 0:  # Выбран режим "Hand"
            auto_container.visible = False
            middle_row.visible = True  # Показываем вкладки workflow
            if workflow_tabs.selected_index == 0:
                input_container.visible = True
                view_container.visible = False
            else:
                input_container.visible = False
                view_container.visible = True
        else:  # Выбран режим "Auto"
            auto_container.visible = True
            input_container.visible = False
            view_container.visible = False
            middle_row.visible = False  # Скрываем вкладки workflow
        
        # Форсируем обновление UI
        page.update()
    
    # Создаем вкладки для переключения между режимами
    workflow_tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Ввод границ"),
            ft.Tab(text="Выравнивание"),
        ],
        on_change=switch_workflow_mode
    )
    
    # Создаем кнопки режима
    mode_selector = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Hand"),
            ft.Tab(text="Auto"),
        ],
        on_change=switch_hand_auto_mode
    )
    
    # Создаем содержимое для всех режимов
    editor_content = create_main_page_content(page, state)
    view_content = create_view_page_content(page, image_stack_left, image_stack_right, state)
    auto_content = create_auto_page_content(page)
    
    # Помещаем содержимое в контейнеры
    input_container.content = editor_content
    view_container.content = view_content
    auto_container.content = auto_content
    
    # Создаем верхний ряд с переключателем режимов слева
    top_row = ft.Row([
        mode_selector
    ], alignment=ft.MainAxisAlignment.START)
    
    # Средний ряд с вкладками
    middle_row = ft.Row([workflow_tabs], alignment=ft.MainAxisAlignment.CENTER)
    
    # Основной макет
    main_layout = ft.Column([
        top_row,
        middle_row,
        input_container,
        view_container,
        auto_container,
    ], expand=True)
    
    # Устанавливаем основной макет на страницу
    page.add(main_layout)

if __name__ == "__main__":
    ft.app(target=main)
import flet as ft
from ..state.app_state import AppState

class ControlPanelComponent:
    """
    Компонент панели управления, содержащий все элементы управления.
    """
    def __init__(self, 
                state: AppState, 
                on_upload=None, 
                on_clear=None, 
                on_save=None, 
                on_load=None, 
                on_grid_toggle=None):
        """
        Инициализирует панель управления.
        
        Args:
            state: Объект состояния приложения
            on_upload: Обработчик нажатия кнопки загрузки изображения
            on_clear: Обработчик нажатия кнопки очистки
            on_save: Обработчик нажатия кнопки сохранения
            on_load: Обработчик нажатия кнопки загрузки
            on_grid_toggle: Обработчик переключения отображения сетки
        """
        self.state = state
        
        # Создаем селектор границы
        self.border_selector = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Верх", icon=ft.icons.ARROW_UPWARD),
                ft.Tab(text="Низ", icon=ft.icons.ARROW_DOWNWARD),
                ft.Tab(text="Лево", icon=ft.icons.ARROW_BACK),
                ft.Tab(text="Право", icon=ft.icons.ARROW_FORWARD),
            ],
            on_change=self._handle_border_change,
            width=260
        )
        
        # Создаем кнопки управления
        self.upload_button = ft.ElevatedButton(
            "Загрузить изображение",
            icon=ft.icons.UPLOAD_FILE,
            on_click=on_upload if on_upload else lambda _: None
        )
        
        self.clear_button = ft.ElevatedButton(
            "Очистить точки",
            icon=ft.icons.DELETE,
            on_click=on_clear if on_clear else lambda _: None,
            disabled=True  # Изначально кнопка неактивна
        )
        
        self.save_button = ft.ElevatedButton(
            "Сохранить точки",
            icon=ft.icons.SAVE,
            on_click=on_save if on_save else lambda _: None,
            disabled=True  # Изначально кнопка неактивна
        )
        
        self.load_button = ft.ElevatedButton(
            "Загрузить точки",
            icon=ft.icons.FOLDER_OPEN,
            on_click=on_load if on_load else lambda _: None
        )
        
        # Создаем чекбокс для отображения сетки
        self.show_grid_checkbox = ft.Checkbox(
            label="Показать сетку",
            value=False,
            disabled=True,  # Изначально чекбокс неактивен
            on_change=on_grid_toggle if on_grid_toggle else lambda _: None
        )
        
        # Создаем контейнер для отображения координат точек
        self.coords_container = ft.Container(
            content=ft.Text("Нет точек"),
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            padding=10,
            bgcolor=ft.colors.WHITE,
            width=400,
            height=150,
            alignment=ft.alignment.top_left,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            expand=True
        )
    
    def _handle_border_change(self, e):
        """Обработчик изменения выбранной границы"""
        self.state.current_border = list(self.state.edge_points_lists.keys())[e.control.selected_index]
    
    def update_coords_text(self):
        """Обновляет текст с координатами точек"""
        points_text = ""
        
        for border_name, points in self.state.edge_points_lists.items():
            if points:
                points_text += f"{border_name}: {', '.join([str(p) for p in points])}\n"
        
        if points_text:
            self.coords_container.content = ft.Text(points_text)
        else:
            self.coords_container.content = ft.Text("Нет точек")
    
    def update_button_states(self):
        """Обновляет состояние кнопок в зависимости от наличия точек"""
        has_points = any(len(points) > 0 for points in self.state.edge_points_lists.values())
        enough_points = self.state.check_points()
        
        # Обновляем состояние кнопок
        self.clear_button.disabled = not has_points
        self.save_button.disabled = not has_points
        
        # Обновляем состояние чекбокса
        self.show_grid_checkbox.disabled = not enough_points
    
    def set_handlers(self, 
                    on_upload=None, 
                    on_clear=None, 
                    on_save=None, 
                    on_load=None, 
                    on_grid_toggle=None):
        """
        Устанавливает обработчики событий для элементов управления.
        Это позволяет установить обработчики после создания объекта.
        
        Args:
            on_upload: Обработчик нажатия кнопки загрузки изображения
            on_clear: Обработчик нажатия кнопки очистки
            on_save: Обработчик нажатия кнопки сохранения
            on_load: Обработчик нажатия кнопки загрузки
            on_grid_toggle: Обработчик переключения отображения сетки
        """
        if on_upload:
            self.upload_button.on_click = on_upload
        
        if on_clear:
            self.clear_button.on_click = on_clear
            
        if on_save:
            self.save_button.on_click = on_save
            
        if on_load:
            self.load_button.on_click = on_load
            
        if on_grid_toggle:
            self.show_grid_checkbox.on_change = on_grid_toggle 
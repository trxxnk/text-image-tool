import flet as ft

class FilePickerManager:
    """
    Управляет FilePicker'ами для выбора и сохранения файлов.
    """
    def __init__(self, page: ft.Page):
        """
        Инициализирует менеджер FilePicker'ов.
        
        Args:
            page (ft.Page): Объект страницы
        """
        self.page = page
        self.image_picker = ft.FilePicker()
        self.save_picker = ft.FilePicker()
        self.load_picker = ft.FilePicker()
        
        # Добавляем FilePicker'ы на страницу
        page.overlay.extend([self.image_picker, self.save_picker, self.load_picker])
    
    def pick_image(self, on_result):
        """
        Открывает диалог выбора изображения.
        
        Args:
            on_result (function): Функция-обработчик результата выбора
        """
        self.image_picker.on_result = on_result
        self.image_picker.pick_files(
            allowed_extensions=["png", "jpg", "jpeg", "bmp", "gif"]
        )
    
    def save_points(self, on_result):
        """
        Открывает диалог сохранения точек.
        
        Args:
            on_result (function): Функция-обработчик результата сохранения
        """
        self.save_picker.on_result = on_result
        self.save_picker.save_file(
            allowed_extensions=["json"],
            file_name="points.json"
        )
    
    def load_points(self, on_result):
        """
        Открывает диалог загрузки точек.
        
        Args:
            on_result (function): Функция-обработчик результата загрузки
        """
        self.load_picker.on_result = on_result
        self.load_picker.pick_files(
            allowed_extensions=["json"]
        )
    
    def save_image(self, on_result):
        """
        Открывает диалог сохранения изображения.
        
        Args:
            on_result (function): Функция-обработчик результата сохранения
        """
        self.save_picker.on_result = on_result
        self.save_picker.save_file(
            allowed_extensions=["png", "jpg", "jpeg", "tif", "tiff"],
            file_name="processed_image.png"
        ) 
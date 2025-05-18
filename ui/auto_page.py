import flet as ft

def create_auto_page_content(page: ft.Page, workflow_tabs, mode_selector):
    """
    Создает содержимое для автоматического режима выравнивания текста.
    
    Args:
        page: Объект страницы
        workflow_tabs: Вкладки для переключения между режимами
        mode_selector: Селектор режима работы
        
    Returns:
        Container: Содержимое страницы автоматического режима
    """
    
    # Создаем надпись "В разработке"
    message = ft.Text(
        "В разработке . . . :-)",
        size=24,
        color=ft.colors.GREY,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER
    )
    
    # Создаем контейнер, который центрирует сообщение на экране
    content = ft.Container(
        content=message,
        alignment=ft.alignment.center,
        expand=True
    )
    
    return content 
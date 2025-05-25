import flet as ft
from typing import Callable
from ..state.app_state import AppState
from ..utils.image_utils import add_watermark
from ..components.image_display import ImageDisplay

def show_alert(page: ft.Page, message: str):
    """Показывает диалог с предупреждением"""
    def on_click(_):
        page.dialog.open = False # TODO: св-ва page.dialog нет
        page.update()
        
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
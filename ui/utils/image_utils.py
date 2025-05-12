import cv2
import tempfile

def add_watermark(image_path: str) -> str:
    """Добавляет водяной знак на изображение"""
    # Загружаем изображение
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Ошибка при загрузке изображения для водяного знака")
        
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
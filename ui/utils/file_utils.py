import json
from datetime import datetime
from typing import Dict, List, Tuple

def save_points_to_json(points: Dict[str, List[Tuple[int, int]]], image_path: str, file_path: str) -> None:
    """Сохраняет точки в JSON файл"""
    save_data = {
        "points": points,
        "image_path": image_path,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2)

def load_points_from_json(file_path: str) -> Dict:
    """Загружает точки из JSON файла"""
    with open(file_path, 'r', encoding='utf-8') as f:
        load_data = json.load(f)
    return load_data
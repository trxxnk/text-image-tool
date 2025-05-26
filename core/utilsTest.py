import numpy as np
from scipy.interpolate import CubicSpline
from scipy.interpolate import RegularGridInterpolator

class CvColors:
    # Basic colors (BGR format)
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    YELLOW = (0, 255, 255)
    CYAN = (255, 255, 0)
    MAGENTA = (255, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Additional colors
    ORANGE = (0, 165, 255)
    PURPLE = (128, 0, 128)
    GRAY = (128, 128, 128)
    PINK = (203, 192, 255)

def preprocess_edges_from_main(edge_top, edge_bottom, edge_left, edge_right):
    # 1. Сортировка top и bottom по X
    edge_top = sorted(edge_top, key=lambda p: p[0])
    edge_bottom = sorted(edge_bottom, key=lambda p: p[0])

    # 2. Сортировка left и right по Y
    edge_left = sorted(edge_left, key=lambda p: p[1], reverse=True)
    edge_right = sorted(edge_right, key=lambda p: p[1], reverse=True)

    # 3. Приведение к согласованным крайним точкам

    # TL (top-left)
    tl = edge_top[0]
    if edge_left[-1] != tl:
        edge_left.append(tl)

    # TR (top-right)
    tr = edge_top[-1]
    if edge_right[-1] != tr:
        edge_right.append(tr)

    # BL (bottom-left)
    bl = edge_bottom[0]
    if edge_left[0] != bl:
        edge_left.insert(0, bl)

    # BR (bottom-right)
    br = edge_bottom[-1]
    if edge_right[0] != br:
        edge_right.insert(0, br)

    return edge_top, edge_bottom, edge_left, edge_right


def create_natural_spline(points: list[tuple|list[float, float]]):
    """Создает натурально-параметризованный кубический сплайн"""
    points = np.array(points)
    
    # Проверка на пустые входные данные
    if len(points) < 2:
        raise ValueError("Для создания сплайна нужно минимум 2 точки")
    
    # Вычисление параметрического расстояния между точками
    diffs = np.diff(points, axis=0)
    distances = np.sqrt(np.sum(diffs**2, axis=1))
    t = np.insert(np.cumsum(distances), 0, 0)
    t_normalized = t / t[-1] if t[-1] != 0 else t
    
    # Проверка на дубликаты и близкие значения параметра
    eps = 1e-10
    unique_indices = [0]
    
    for i in range(1, len(t_normalized)):
        if t_normalized[i] - t_normalized[unique_indices[-1]] > eps:
            unique_indices.append(i)
    
    # Используем только уникальные значения
    t_unique = t_normalized[unique_indices]
    points_unique = points[unique_indices]
    
    # Если осталось менее 2 уникальных точек, не можем построить сплайн
    if len(t_unique) < 2:
        # Возвращаем линейную интерполяцию (константу) в этом случае
        def constant_func(t):
            if np.isscalar(t):
                return np.array([points[0]])
            return np.array([points[0]] * len(t))
        return constant_func
    
    # Построение сплайнов для координат x и y
    cs_x = CubicSpline(t_unique, points_unique[:, 0], bc_type='natural')
    cs_y = CubicSpline(t_unique, points_unique[:, 1], bc_type='natural')

    def spline_func(t):
        x = cs_x(t)
        y = cs_y(t)
        return np.column_stack([x, y]) if np.ndim(x) == 1 else np.array([[x, y]])

    return spline_func

def build_mesh_function(edge_top, edge_bottom, edge_left, edge_right):
    """Возвращает функцию mesh_point(s, t)"""
    spline_top = create_natural_spline(edge_top)
    spline_bottom = create_natural_spline(edge_bottom)
    spline_left = create_natural_spline(edge_left)
    spline_right = create_natural_spline(edge_right)

    P00 = spline_bottom(0)  # Левый нижний
    P10 = spline_bottom(1)  # Правый нижний
    P01 = spline_top(0)     # Левый верхний
    P11 = spline_top(1)     # Правый верхний

    def mesh_point(s, t):
        term1 = (1-t)*spline_bottom(s) + t*spline_top(s)
        term2 = (1-s)*spline_left(t) + s*spline_right(t)
        term3 = (1-t)*(1-s)*P00 + (1-t)*s*P10 + t*(1-s)*P01 + t*s*P11
        return (term1 + term2 - term3)[0]

    return mesh_point


def build_vectorized_mesh_function(edge_top, edge_bottom, edge_left, edge_right):
    """Возвращает векторизованную функцию mesh_points(s_array, t_array)"""    
    spline_top = create_natural_spline(edge_top)
    spline_bottom = create_natural_spline(edge_bottom)
    spline_left = create_natural_spline(edge_left)
    spline_right = create_natural_spline(edge_right)

    # Получение угловых точек
    P00 = spline_bottom(0)[0]  # Левый нижний
    P10 = spline_bottom(1)[0]  # Правый нижний
    P01 = spline_top(0)[0]     # Левый верхний
    P11 = spline_top(1)[0]     # Правый верхний

    def mesh_points(s_array, t_array):
        # Преобразование в массивы NumPy если они еще не являются ими
        s = np.asarray(s_array)
        t = np.asarray(t_array)
        
        # Сохранение оригинальной формы для последующего восстановления
        original_shape = s.shape
        
        # Приведение к 1D массивам для обработки
        s_flat = s.flatten()
        t_flat = t.flatten()
        
        # Создание результирующего массива
        result = np.zeros((len(s_flat), 2))
        
        # Вычисление значений для всех точек сплайна
        bottom_vals = np.array([spline_bottom(si)[0] for si in s_flat])
        top_vals = np.array([spline_top(si)[0] for si in s_flat])
        left_vals = np.array([spline_left(ti)[0] for ti in t_flat])
        right_vals = np.array([spline_right(ti)[0] for ti in t_flat])
        
        # Расчет по формуле транзитивной интерполяции
        for i in range(len(s_flat)):
            si, ti = s_flat[i], t_flat[i]
            term1 = (1-ti) * bottom_vals[i] + ti * top_vals[i]
            term2 = (1-si) * left_vals[i] + si * right_vals[i]
            term3 = (1-ti)*(1-si)*P00 + (1-ti)*si*P10 + ti*(1-si)*P01 + ti*si*P11
            result[i] = term1 + term2 - term3
        
        # Восстановление оригинальной формы
        map_x = result[:, 0].reshape(original_shape)
        map_y = result[:, 1].reshape(original_shape)
        
        return map_x, map_y

    return mesh_points

def build_fast_mesh_function(edge_top, edge_bottom, edge_left, edge_right):
    """
    Создает быструю функцию меша для применения к массиву точек.
    Возвращает функцию, которая принимает весь массив нормализованных координат.
    """
    # Создаем сплайны для всех границ
    spline_top = create_natural_spline(edge_top)
    spline_bottom = create_natural_spline(edge_bottom)
    spline_left = create_natural_spline(edge_left)
    spline_right = create_natural_spline(edge_right)

    # Вычисляем угловые точки напрямую из входных данных
    # Это более надежно, чем использовать сплайны для краевых точек
    P00 = np.array(edge_bottom[0])   # Левый нижний
    P10 = np.array(edge_bottom[-1])  # Правый нижний
    P01 = np.array(edge_top[0])      # Левый верхний
    P11 = np.array(edge_top[-1])     # Правый верхний

    print(f"Угловые точки:")
    print(f"P00 (левый нижний): {P00}")
    print(f"P10 (правый нижний): {P10}")
    print(f"P01 (левый верхний): {P01}")
    print(f"P11 (правый верхний): {P11}")

    # Предвычисляем точки сплайнов для более быстрой интерполяции
    num_samples = 100  # Количество точек в предвычисленных сплайнах
    s_values = np.linspace(0, 1, num_samples)
    t_values = np.linspace(0, 1, num_samples)
    
    # Используем предвычисленные точки для каждой границы
    top_points = np.array([spline_top(s)[0] for s in s_values])
    bottom_points = np.array([spline_bottom(s)[0] for s in s_values])
    left_points = np.array([spline_left(t)[0] for t in t_values])
    right_points = np.array([spline_right(t)[0] for t in t_values])

    def apply_mesh_to_grid(s:np.ndarray, t:np.ndarray):
        """
        Векторизованная функция применения меша к массиву точек.
        
        Args:
            normalized_grid: массив нормализованных координат (t,s) размера [height, width, 2]
                t - вертикальная координата (0 вверху, 1 внизу)
                s - горизонтальная координата (0 слева, 1 справа)
            
        Returns:
            массив преобразованных точек размера [height, width, 2]
        """
        # Извлекаем t и s координаты
        # t = normalized_grid[..., 0]  # Вертикальная координата [0,1] (0 вверху, 1 внизу)
        # s = normalized_grid[..., 1]  # Горизонтальная координата [0,1]
        
        height, width = t.shape
        
        # Создаем интерполирующие функции для быстрого доступа к точкам
        # Используем линейную интерполяцию для скорости
        
        # Создаем регулярные сетки для интерполяции
        # Интерполяторы для верхней и нижней границ (функция от s)
        interp_top_x = RegularGridInterpolator((s_values,), top_points[:, 0], bounds_error=False, fill_value=None)
        interp_top_y = RegularGridInterpolator((s_values,), top_points[:, 1], bounds_error=False, fill_value=None)
        interp_bottom_x = RegularGridInterpolator((s_values,), bottom_points[:, 0], bounds_error=False, fill_value=None)
        interp_bottom_y = RegularGridInterpolator((s_values,), bottom_points[:, 1], bounds_error=False, fill_value=None)
        
        # Интерполяторы для левой и правой границ (функция от t)
        interp_left_x = RegularGridInterpolator((t_values,), left_points[:, 0], bounds_error=False, fill_value=None)
        interp_left_y = RegularGridInterpolator((t_values,), left_points[:, 1], bounds_error=False, fill_value=None)
        interp_right_x = RegularGridInterpolator((t_values,), right_points[:, 0], bounds_error=False, fill_value=None)
        interp_right_y = RegularGridInterpolator((t_values,), right_points[:, 1], bounds_error=False, fill_value=None)

        # Подготовка входных данных для интерполяторов
        s_flat = s.reshape(-1, 1)
        t_flat = t.reshape(-1, 1)

        # Интерполяция по s (горизонтальная координата)
        bottom_x = interp_bottom_x(s_flat).reshape(height, width)
        bottom_y = interp_bottom_y(s_flat).reshape(height, width)
        top_x = interp_top_x(s_flat).reshape(height, width)
        top_y = interp_top_y(s_flat).reshape(height, width)

        # Интерполяция по t (вертикальная координата)
        left_x = interp_left_x(t_flat).reshape(height, width)
        left_y = interp_left_y(t_flat).reshape(height, width)
        right_x = interp_right_x(t_flat).reshape(height, width)
        right_y = interp_right_y(t_flat).reshape(height, width)

        # Применение формулы транзитивной интерполяции
        
        # Вычисляем первый член уравнения (интерполяция между верхней и нижней границами)
        term1_x = (1 - t) * bottom_x + t * top_x
        term1_y = (1 - t) * bottom_y + t * top_y

        # Вычисляем второй член уравнения (интерполяция между левой и правой границами)
        term2_x = (1 - s) * left_x + s * right_x
        term2_y = (1 - s) * left_y + s * right_y

        # Вычисляем третий член уравнения (билинейная интерполяция угловых точек)
        term3_x = (1 - t) * (1 - s) * P00[0] + (1 - t) * s * P10[0] + t * (1 - s) * P01[0] + t * s * P11[0]
        term3_y = (1 - t) * (1 - s) * P00[1] + (1 - t) * s * P10[1] + t * (1 - s) * P01[1] + t * s * P11[1]

        # Итоговый результат по формуле: term1 + term2 - term3
        result_x = term1_x + term2_x - term3_x
        result_y = term1_y + term2_y - term3_y

        # Возвращаем массив точек, где для каждой точки (i, j) получаем координаты (x, y)
        return np.stack([result_x, result_y], axis=-1).astype(np.float32)
        
    return apply_mesh_to_grid
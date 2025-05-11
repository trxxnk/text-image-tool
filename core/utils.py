import numpy as np
from scipy.interpolate import CubicSpline

def preprocess_edges(edge_top, edge_bottom, edge_left, edge_right):
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
    diffs = np.diff(points, axis=0)
    distances = np.sqrt(np.sum(diffs**2, axis=1))
    t = np.insert(np.cumsum(distances), 0, 0)
    t_normalized = t / t[-1] if t[-1] != 0 else t

    cs_x = CubicSpline(t_normalized, points[:, 0], bc_type='natural')
    cs_y = CubicSpline(t_normalized, points[:, 1], bc_type='natural')

    def spline_func(t):
        x = cs_x(t)
        y = cs_y(t)
        return np.column_stack([x, y])

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
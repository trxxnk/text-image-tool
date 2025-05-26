import numpy as np
import cv2


def create_coordinate_grid(height, width):
    """
    Creates a coordinate grid for an image of specified dimensions.
    
    Args:
        height: Height of the image
        width: Width of the image
    
    Returns:
        grid: A grid of coordinates with shape [height, width, 2]
    """
    grid = np.mgrid[height-1:-1:-1, 0:width:1].swapaxes(0, 2).swapaxes(0, 1)
    return grid


def normalize_grid_coordinates(grid, width, height):
    """
    Normalizes grid coordinates to the range [0,1] for both s and t parameters.
    
    Args:
        grid: The coordinate grid to normalize
        width: Width of the image
        height: Height of the image
    
    Returns:
        normalized_grid: Normalized grid where coordinates are in [0,1] range
    """
    normalized_grid = grid.copy().astype(np.float32)
    normalized_grid[..., 1] /= (width-1)  # s coordinate (horizontal)
    normalized_grid[..., 0] /= (height-1)  # t coordinate (vertical)
    return normalized_grid


def compute_remap_maps(mesh_func, normalized_grid):
    """
    Computes the map_x and map_y arrays for cv2.remap based on the mesh function.
    
    Args:
        mesh_func: The mesh transformation function
        normalized_grid: Normalized grid coordinates
    
    Returns:
        map_x, map_y: Arrays ready to be used with cv2.remap
    """
    res = mesh_func(normalized_grid[..., 1], normalized_grid[..., 0])
    map_y = res[..., 1]
    map_x = res[..., 0]
    map_x = map_x.astype(np.float32)
    map_y = map_y.astype(np.float32)
    return map_x, map_y


def apply_remap(image, map_x, map_y, interpolation=cv2.INTER_CUBIC, border_mode=cv2.BORDER_CONSTANT):
    """
    Applies the cv2.remap function with the given parameters.
    
    Args:
        image: Input image
        map_x: X coordinate mapping
        map_y: Y coordinate mapping
        interpolation: Interpolation method
        border_mode: Border handling mode
    
    Returns:
        result: Remapped image
    """
    result = cv2.remap(image,
                      map_x,
                      map_y,
                      interpolation=interpolation,
                      borderMode=border_mode)
    return result


def get_log_thickness(height, width):
    """
    Calculates appropriate line thickness based on image dimensions.
    
    Args:
        height: Image height
        width: Image width
    
    Returns:
        thickness: Appropriate line thickness
    """
    size_factor = np.log10(height * width)
    return max(1, int(size_factor))


def visualize_grid(image, mesh_func, n_points=10, color_horizontal=None, color_vertical=None):
    """
    Visualizes the transformation grid on an image.
    
    Args:
        image: The original image to draw on
        mesh_func: The mesh transformation function
        n_points: Number of grid lines in each direction
        color_horizontal: Color for horizontal grid lines (s-lines)
        color_vertical: Color for vertical grid lines (t-lines)
    
    Returns:
        visualization: Image with grid visualization
    """
    if color_horizontal is None:
        color_horizontal = (0, 0, 255)  # Red by default
    if color_vertical is None:
        color_vertical = (255, 0, 0)  # Blue by default
        
    visualization = image.copy()
    height, width = image.shape[:2]
    cur_thickness = get_log_thickness(height, width)
    
    test_params = []
    
    # Horizontal grid lines (constant s)
    for s in np.linspace(0, 1, n_points):
        test_params.append(
            (s * np.ones(n_points), np.linspace(0, 1, n_points), color_horizontal)
        )
    
    # Vertical grid lines (constant t)
    for t in np.linspace(0, 1, n_points):
        test_params.append(
            (np.linspace(0, 1, n_points), t * np.ones(n_points), color_vertical)
        )
    
    # Draw grid lines
    for s, t, color in test_params:
        # Convert 1D arrays to 2D
        s_2d = s.reshape(1, -1)
        t_2d = t.reshape(1, -1)
        
        # Get transformed coordinates
        res = mesh_func(s_2d, t_2d)
        x = res[..., 0]
        y = res[..., 1]
        
        # Create point array for drawing
        points = np.array([x.flatten(), y.flatten()]).T
        points = points.reshape((-1, 1, 2)).astype(np.int32)
        cv2.polylines(visualization, [points], False, color, cur_thickness)
    
    return visualization


def visualize_boundary_points(image, edges, colors=None, thickness_factor=2):
    """
    Visualizes boundary points on an image.
    
    Args:
        image: The image to draw on
        edges: Dictionary or list of edge points lists
        colors: List of colors for each edge
        thickness_factor: Factor to multiply the base thickness
    
    Returns:
        visualization: Image with boundary points visualization
    """
    visualization = image.copy()
    height, width = image.shape[:2]
    
    base_thickness = get_log_thickness(height, width)
    circle_radius = int(base_thickness * thickness_factor)
    point_thickness = circle_radius * 2
    
    # Default colors if none provided
    if colors is None:
        colors = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (0, 165, 255)]  # R, B, G, O
    
    if isinstance(edges, dict):
        # If edges is a dictionary, convert to list
        edge_lists = [edges[key] for key in sorted(edges.keys())]
    else:
        edge_lists = edges
    
    for i, points in enumerate(edge_lists):
        color = colors[i % len(colors)]
        for point in points:
            x, y = int(point[0]), int(point[1])
            cv2.circle(visualization, (x, y), circle_radius, color, point_thickness)
    
    return visualization 
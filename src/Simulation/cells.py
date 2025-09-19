import numpy as np
from abc import ABC, abstractmethod
import logging


class CellFactory:
    """
    Uses a factory pattern to instantiate cells by type.
    This keeps creation logic clear and allows easy extension for new cell types.
    """
    def __init__(self):
        self._cell_types = {}  # Maps type keys (e.g., "triangle") to their respective classes.
        logging.info("CellFactory initialized.")

    def register(self, key, cell_class):
        """
        Registers a cell class under a given key.

        Parameters:
        - key (str): Identifies the cell type.
        - cell_class (class): The class to instantiate for this type.
        """
        self._cell_types[key] = cell_class
        logging.info(f"Registered cell type: {key}")

    def __call__(self, key, point_ids, idx, points):
        """
        Instantiates a cell of the requested type.

        Parameters:
        - key (str): Specifies which cell type to create.
        - point_ids (list): Indices of the cell's vertices in the mesh.
        - idx (int): Unique index for the cell.
        - points (ndarray): Coordinates of the cell's vertices.

        Returns:
        - A new instance of the cell class corresponding to the given key.
        """
        logging.info(f"Creating cell of type {key} with index {idx}.")
        return self._cell_types[key](point_ids, idx, points)


class Cell(ABC):
    """
    Base class for all cells. Provides shared attributes and structure for computing neighbors.
    """
    def __init__(self, point_ids, idx, points):
        self._point_ids = point_ids
        self._idx = idx
        self.midpoint = np.mean(points, axis=0)
        self.neighbors = [-1 for _ in point_ids]
        self._points = points
        # Defines a velocity field that depends on midpoint coordinates,
        # useful for simulating flow behavior in 2D.
        self.velocity = np.array([
            self.midpoint[1] - 0.2 * self.midpoint[0],
            -self.midpoint[0],
            0.0
        ])
        logging.debug(f"Cell {idx} initialized with midpoint {self.midpoint}.")

    def compute_neighbors(self, cells):
        """
        Placeholder for neighbor logic. Subclasses specify how neighbors are determined.
        """
        pass

    @abstractmethod
    def __str__(self):
        """
        Must return a string representation of the cell.
        Subclasses handle the details.
        """
        pass


class Triangle(Cell):
    """
    A triangular cell with methods to calculate area, normals, and neighbor relationships.
    """
    def __init__(self, point_ids, idx, points):
        """
        Computes the area and outward normals for a triangular cell.

        Parameters:
        - point_ids (list): Indices of the triangle's vertices.
        - idx (int): Unique index of this triangle in the mesh.
        - points (ndarray): Coordinates of the triangle's vertices.

        Raises:
        - ValueError: If the cell is not exactly three points.
        """
        super().__init__(point_ids, idx, points)
        self.type = "triangle"
        self.coords = self._points

        # Places oil mostly around (0.35, 0.45) to mimic an initial spill location.
        x_start, y_start = 0.35, 0.45
        self.oil_value = np.exp(
            -((self.midpoint[0] - x_start) ** 2 + (self.midpoint[1] - y_start) ** 2) / 0.01
        )

        if len(point_ids) != 3:
            raise ValueError("Triangle cells require three point indices.")
        if points.shape[0] != 3:
            raise ValueError("The points array must be shape (3, 2).")

        # Uses a determinant-based formula for 2D triangular area.
        self.area = 0.5 * abs(
            (points[0][0] - points[2][0]) * (points[1][1] - points[0][1])
            - (points[0][0] - points[1][0]) * (points[2][1] - points[0][1])
        )

        # Normals point outward, one for each edge of the triangle.
        self.normals = [[-1, -1, -1] for _ in point_ids]
        coords_list = list(points)
        coords_cycle = coords_list[1:] + [coords_list[0]]

        for i, (p1, p2) in enumerate(zip(coords_list, coords_cycle)):
            v = np.array(p2) - np.array(p1)
            normal = np.array([-v[1], v[0], 0.0])
            # Flip the direction if this normal points into the triangle.
            if np.dot(normal, p1 - self.midpoint) < 0:
                normal *= -1
            # Match the normal's length to the edge length for more accurate flux calculations.
            self.normals[i] = normal / np.linalg.norm(normal) * np.linalg.norm(v)
        logging.info(f"Triangle {idx} initialized with area {self.area} and oil_value {self.oil_value}.")

    def __str__(self):
        return f"Triangle: {self.neighbors}"

    def compute_neighbors(self, cells):
        """
        Finds triangles (or lines) that share two vertices with this triangle.

        Parameters:
        - cells (list): All cells in the mesh.
        """
        my_points = set(self._point_ids)
        for idx, cell in enumerate(cells):
            if len(my_points & set(cell._point_ids)) == 2:
                pts = list(self._point_ids)
                pts_plus = pts[1:] + [pts[0]]
                # We check each pair of consecutive points in this triangle
                # to see if they match those in the neighbor.
                for i, (p, pplus) in enumerate(zip(pts, pts_plus)):
                    if p in cell._point_ids and pplus in cell._point_ids:
                        self.neighbors[i] = idx
                        logging.debug(f"Triangle {self._idx} assigned neighbor {idx}.")
                        break


class Line(Cell):
    """
    A line cell, generally used to denote boundaries or edges in the mesh.
    """
    def __init__(self, point_ids, idx, points):
        super().__init__(point_ids, idx, points)
        self.type = "line"
        # Lines are treated as boundaries where oil does not accumulate.
        self.oil_value = 0.0
        logging.info(f"Line {idx} initialized.")

    def compute_neighbors(self, cells):
        """
        No neighbor logic here, but could be extended
        if lines need special boundary handling.
        """
        pass

    def __str__(self):
        return f"Line: {self.neighbors}"

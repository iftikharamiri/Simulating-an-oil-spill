import meshio
from src.Simulation.cells import CellFactory, Triangle, Line
import logging


class Mesh:
    """
    Represents the mesh used in the simulation.

    The Mesh class is responsible for reading a mesh file, initializing cells,
    finding neighbors, and identifying cells within specific areas, such as the fishing area.
    """

    def __init__(self, filename):
        """
        Initializes the Mesh object by reading the mesh file and creating cells.

        Parameters:
            filename (str): Path to the mesh file.

        Raises:
            FileNotFoundError: If the mesh file cannot be found or read.
        """
        mesh = meshio.read(filename)  # Reads the mesh file
        points = mesh.points  # Retrieves the coordinates of mesh points
        cells = mesh.cells  # Retrieves the cell definitions
        self._points = points

        # Initialize the cell factory and register cell types
        factory = CellFactory()
        factory.register("triangle", Triangle)
        factory.register("line", Line)

        self._cells = []

        # Loop through all cell types and add them to the mesh
        for cell_type_and_data in cells:
            cell_type = cell_type_and_data.type
            if cell_type == "vertex":  # Skip vertex cells
                continue
            cellindices = cell_type_and_data.data
            for cell_idx in cellindices:
                # Create and store a new cell
                cell = factory(cell_type, cell_idx, len(self._cells), points[cell_idx, :])
                self._cells.append(cell)

        logging.info(f"Initialized {len(self._cells)} cells from mesh.")

    def find_neighbors(self):
        """
        Calculates and assigns neighbors for all cells in the mesh.

        Neighboring cells share at least two vertices. This is important for
        calculating flux and other simulation properties.
        """
        logging.info("Calculating neighbors for all cells.")
        for cell in self._cells:
            cell.compute_neighbors(self._cells)
        logging.info("Neighbor calculation completed.")

    def cells(self):
        """
        Returns a list of all cells in the mesh.

        Returns:
            list: A list containing all cells.
        """
        return self._cells

    def fishing_cells(self, x_min=0.0, x_max=0.45, y_min=0.0, y_max=0.2):
        """
        Identifies all cells within the fishing area.

        The fishing area is defined by rectangular bounds in the x and y dimensions.
        Only triangular cells are considered for this area.

        Parameters:
            x_min (float): Minimum x-coordinate of the fishing area (default is 0.0).
            x_max (float): Maximum x-coordinate of the fishing area (default is 0.45).
            y_min (float): Minimum y-coordinate of the fishing area (default is 0.0).
            y_max (float): Maximum y-coordinate of the fishing area (default is 0.2).

        Returns:
            list: A list of cells within the fishing area.
        """
        fishing_cells = [
            cell for cell in self._cells
            if cell.type == "triangle" and
            x_min <= cell.midpoint[0] <= x_max and
            y_min <= cell.midpoint[1] <= y_max
        ]
        logging.info(f"Identified {len(fishing_cells)} cells in the fishing area.")
        return fishing_cells

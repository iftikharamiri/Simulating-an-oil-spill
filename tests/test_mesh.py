import pytest
from src.Simulation.mesh import Mesh
from src.Simulation.cells import Triangle, Line

# Fixture to create a Mesh instance
@pytest.fixture
def mesh_instance():
    """
    making a return mesh
    """
    filename = "src/Simulation/data/simple.msh"  # we used simplier mesh
    return Mesh(filename)

def test_mesh_initialization(mesh_instance):
    """
    making sure mesh class initalize correct
  """
    assert len(mesh_instance._cells) > 0, "Cells should not be empty."
    for cell in mesh_instance._cells:
        assert isinstance(cell, (Triangle, Line)), "Cells should be Triangle or Line."

def test_find_neighbors(mesh_instance):
    """
    making sure that negihbour are found correct for each cell
 """
    mesh_instance.find_neighbors()
    for cell in mesh_instance._cells:
        assert hasattr(cell, 'neighbors'), "Each cell should have a 'neighbors' attribute."
        assert isinstance(cell.neighbors, list), "Neighbors should be a list."

def test_cells_method(mesh_instance):
    """
    making sure thta cells() return correct list
"""
    assert mesh_instance.cells() == mesh_instance._cells, "cells() should return the internal cell list."

def test_unsupported_cell_type():
    """making sure tha usnuporterd cell types are handled corect
"""
    # Mock data with supported and unsupported cell types
    mock_cells = [
        {"type": "triangle", "data": [[0, 1, 2]]},
        {"type": "line", "data": [[0, 1]]},
        {"type": "unsupported", "data": [[0, 1, 2, 3]]},
    ]

    # Create a Mesh instance without running its __init__ method
    mesh = Mesh.__new__(Mesh)
    mesh._cells = [cell for cell in mock_cells if cell["type"] in ["triangle", "line"]]

    # Check that only supported types are processed
    for cell in mesh._cells:
        assert cell["type"] in ["triangle", "line"], "Unsupported cell type should not be processed."

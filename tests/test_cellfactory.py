import pytest
from src.Simulation.cells import CellFactory

# Mock classes to test CellFactory
class MockCell:
    def __init__(self, point_ids, idx, points):
        self.point_ids = point_ids
        self.idx = idx
        self.points = points

@pytest.fixture
def cell_factory():
    """
    Pytest fixture to set up a CellFactory instance for testing.
    """
    factory = CellFactory()
    factory.register("mock", MockCell)
    return factory

@pytest.mark.parametrize(
    "key, point_ids, idx, points, expected_type",
    [
        ("mock", [1, 2, 3], 101, [[0, 0], [1, 0], [0, 1]], MockCell),  # Valid case
    ]
)
def test_cell_factory_instantiation(cell_factory, key, point_ids, idx, points, expected_type):
    """
    Test that CellFactory instantiates the correct cell type.
    """
    # Act
    cell = cell_factory(key, point_ids, idx, points)

    # Assert
    assert isinstance(cell, expected_type)
    assert cell.point_ids == point_ids
    assert cell.idx == idx
    assert cell.points == points

def test_cell_factory_invalid_key(cell_factory):
    """
    Test that CellFactory raises KeyError for invalid keys.
    """
    with pytest.raises(KeyError) as excinfo:
        cell_factory("non_existent_key", [1, 2, 3], 101, [[0, 0], [1, 0], [0, 1]])

    assert str(excinfo.value) == "'non_existent_key'"

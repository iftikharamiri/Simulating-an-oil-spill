import pytest
import numpy as np
from src.Simulation.cells import Cell

class TestCell(Cell):
    def __str__(self):
        return f"testCell with id {self._idx}"

# Fixture for shared test data
@pytest.fixture
def cell_data():
    point_ids = [0, 1, 2]
    idx = 42
    points = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
    return point_ids, idx, points

@pytest.mark.parametrize(
    "point_ids, idx, points, expected_midpoint, expected_neighbors",
    [
        (
            [0, 1, 2],
            42,
            np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]]),
            [0.5, 0.3333333333333333],
            [-1, -1, -1]
        ),
        (
            [3, 4, 5],
            99,
            np.array([[1.0, 1.0], [2.0, 1.0], [1.5, 2.0]]),
            [1.5, 1.3333333333333333],
            [-1, -1, -1]
        )
    ]
)
def test_cell_initialization(point_ids, idx, points, expected_midpoint, expected_neighbors):
    # Create a TestCell instance
    cell = TestCell(point_ids, idx, points)

    # Validate attributes
    assert cell._point_ids == point_ids
    assert cell._idx == idx
    np.testing.assert_array_equal(cell._points, points)
    np.testing.assert_almost_equal(cell.midpoint, expected_midpoint)
    assert len(cell.neighbors) == len(point_ids)
    assert all(n == expected_neighbors[i] for i, n in enumerate(cell.neighbors))

@pytest.mark.parametrize(
    "point_ids, idx, points, expected_str",
    [
        (
            [0, 1, 2],
            42,
            np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]]),
            "testCell with id 42"
        ),
        (
            [3, 4, 5],
            99,
            np.array([[1.0, 1.0], [2.0, 1.0], [1.5, 2.0]]),
            "testCell with id 99"
        )
    ]
)
def test_cell_abstract_method(point_ids, idx, points, expected_str):
    # Create a TestCell instance
    cell = TestCell(point_ids, idx, points)

    # Test the __str__ method
    assert str(cell) == expected_str

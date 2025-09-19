import pytest
from src.Simulation.cells import *

class TestCell(Cell):
    def __str__(self):
        return f"testCell with id {self._idx}"

# Fixture data
@pytest.fixture
def cell_data():
    point_ids = [0, 1, 2]
    idx = 42
    points = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
    return point_ids, idx, points


# Testcell initialization
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
    """
    making sure testcell initlaizes correctly with given parameter
    """
    cell = TestCell(point_ids, idx, points)

    # validate the attribute 
    assert cell._point_ids == point_ids
    assert cell._idx == idx
    np.testing.assert_array_equal(cell._points, points)
    np.testing.assert_almost_equal(cell.midpoint, expected_midpoint)
    assert len(cell.neighbors) == len(point_ids)
    assert all(n == expected_neighbors[i] for i, n in enumerate(cell.neighbors))


# __str__ method

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
def test_cell_str(point_ids, idx, points, expected_str):
    """ 
    making sure the __str__ method return correct
    """
    cell = TestCell(point_ids, idx, points)

    # Test the __str__ method
    assert str(cell) == expected_str



#Trisngle area

@pytest.mark.parametrize(
    "point_ids, idx, points, expected_area",
    [
        (
            [0, 1, 2],
            42,
            np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]]),
            0.5
        ),
        (
            [3, 4, 5],
            99,
            np.array([[1.0, 1.0, 0.0], [2.0, 1.0, 0.0], [1.5, 2.0, 0.0]]),
            0.5
        )
    ]
)
def test_triangle_area(point_ids, idx, points, expected_area):
    """
    making sure traingale area calcualted correct
    """
    triangle = Triangle(point_ids, idx, points)

    assert triangle.area == pytest.approx(expected_area, rel=1e-3)



# Triangle neighbour
# they are not sharing the points, expected to get no neighbour [-1]
@pytest.mark.parametrize(
    "point_ids, idx, points, neighbor_triangles, expected_neighbors",
    [
        (
            [0, 1, 2],
            42,
            np.array([[67.0, 0.0, 0.0], [1.0, 3.0, 0.0], [0.5, 1.0, 6.0]]),
            [
                Triangle([1, 2, 3], 11, np.array([
                    [1.0, 0.0, 0.0],
                    [0.5, 1.0, 0.0],
                    [1.0, 2.0, 0.0]
                ]))
            ],
            [-1, -1, -1]
        )
    ]
)
def test_triangle_neighbors(point_ids, idx, points, neighbor_triangles, expected_neighbors):
    """
    making sure neighbour handled correctly 
    """
    triangle = Triangle(point_ids, idx, points)

    # Add neighbors
    for neighbor in neighbor_triangles:
        neighbor.compute_neighbors([triangle] + neighbor_triangles)
    
    # expecting to get none [-1] they are not neighbour
    assert triangle.neighbors == expected_neighbors


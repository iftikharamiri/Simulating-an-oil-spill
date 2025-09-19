import pytest
from src.Simulation.cells import Line, np

# Fixture data
@pytest.fixture
def default_line():
   
    point_ids = [0, 1]
    idx = 20
    points = np.array([[0.0, 0.0], [1.0, 0.0]])
    return Line(point_ids, idx, points)

# making sure that point_ids and index are set corectly
@pytest.mark.parametrize(
    "point_ids, idx",
    [
        ([0, 1], 20),
        ([2, 3], 30),
    ],
)
def test_line_point_ids_and_idx(point_ids, idx):
   
    points = np.array([[0.0, 0.0], [1.0, 0.0]])
    line = Line(point_ids, idx, points)

    assert line._point_ids == point_ids 
    assert line._idx == idx

# making sure points are set correctly
@pytest.mark.parametrize(
    "points",
    [
        np.array([[0.0, 0.0], [1.0, 0.0]]),
        np.array([[1.0, 1.0], [2.0, 1.0]]),
    ],
)
def test_line_points(points):
   
    point_ids = [0, 1]
    idx = 20
    line = Line(point_ids, idx, points)

    np.testing.assert_array_equal(line._points, points)

# Tvalue og type
def test_line_type_and_oil_value(default_line):
   
    assert default_line.type == "line"
    assert default_line.oil_value == 0.0



# make sure string is correct
@pytest.mark.parametrize(
    "point_ids, idx, points",
    [
        ([0, 1], 20, np.array([[0.0, 0.0], [1.0, 0.0]])),
        ([2, 3], 30, np.array([[1.0, 1.0], [2.0, 1.0]])),
    ],
)
def test_line_str_representation(point_ids, idx, points):
  
    line = Line(point_ids, idx, points)
    line_str = str(line)

    assert "Line:" in line_str
    assert "-1" in line_str
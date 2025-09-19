import pytest
import toml
import numpy as np
from src.Simulation.solver import Solver

# fixture data
@pytest.fixture
def solver_instance():
    """
    fixture to initialze a solver instance with fake configuration
    """
    mock_config = toml.loads("""
    [settings]
    nSteps = 10
    tStart = 0.0
    tEnd = 1.0

    [geometry]
    meshName = "src/Simulation/data/simple.msh"
    borders = [
        [0.0, 0.45],    # x1, y1
        [0.0, 0.2]      # x2, y2
    ]                 # define where fish are located

    [IO]
    logName = "simulation.log"
    writeFrequency = 2
    """)
    return Solver(mock_config)



@pytest.mark.parametrize("a, b, n, v, expected_flux", [
    (0.8, 0.4, np.array([1.0, 0.0]), np.array([0.5, 0.0]), 0.8 * 0.5),  # Positive flux
    (0.8, 0.4, np.array([-1.0, 0.0]), np.array([0.5, 0.0]), 0.4 * -0.5),  # Negative flux
    (1.0, 0.5, np.array([0.0, 1.0]), np.array([0.0, -0.5]), 0.5 * -0.5),  # Vertical negative flux
    (1.0, 0.5, np.array([0.0, 1.0]), np.array([0.0, 0.5]), 1.0 * 0.5),   # Vertical positive flux
])
def test_flux_function(solver_instance, a, b, n, v, expected_flux):
    """
    testing flux for various secnariuer
"""
    solver = solver_instance
    result = solver.flux_function(a, b, n, v)
    assert np.isclose(result, expected_flux), f"Expected {expected_flux}, got {result}"


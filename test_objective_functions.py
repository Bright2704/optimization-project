import unittest
import tempfile
from pathlib import Path

import numpy as np

from utils.objective_functions import (
    BOUNDS,
    FUNCTIONS,
    SCHWEFEL_PDF_CONSTANT,
    SCHWEFEL_STANDARD_CONSTANT,
    get_bounds,
    get_function,
    griewank,
    paraboloid,
    rastrigin,
    rosenbrock,
    schwefel,
)
from objective_function_report import run_objective_tests


class ObjectiveFunctionTests(unittest.TestCase):
    def test_known_formula_values(self):
        self.assertEqual(paraboloid([1, 2, 3]), 14.0)
        self.assertEqual(rosenbrock([0, 0]), 1.0)
        self.assertAlmostEqual(
            griewank([1, 1]),
            1 + 2 / 4000 - np.cos(1) * np.cos(1 / np.sqrt(2)),
        )
        self.assertAlmostEqual(rastrigin([1, 1]), 2.0)
        self.assertEqual(schwefel([0, 0]), 2 * SCHWEFEL_PDF_CONSTANT)

    def test_known_minimizers(self):
        self.assertEqual(paraboloid(np.zeros(20)), 0.0)
        self.assertEqual(rosenbrock(np.ones(20)), 0.0)
        self.assertEqual(griewank(np.zeros(20)), 0.0)
        self.assertEqual(rastrigin(np.zeros(20)), 0.0)
        self.assertAlmostEqual(
            schwefel(
                np.full(20, 420.9687), constant=SCHWEFEL_STANDARD_CONSTANT
            ),
            0.0,
            delta=3e-4,
        )

    def test_registry_and_bounds_cover_all_functions(self):
        self.assertEqual(set(FUNCTIONS), set(BOUNDS))
        for name, function in FUNCTIONS.items():
            with self.subTest(name=name):
                self.assertIs(get_function(name.upper()), function)
                bounds = get_bounds(name, 20)
                self.assertEqual(len(bounds), 20)
                self.assertTrue(all(bound == BOUNDS[name] for bound in bounds))

    def test_invalid_vectors_are_rejected(self):
        for point in ([], [[1, 2]], [np.nan], [np.inf], [1 + 2j]):
            with self.subTest(point=point):
                with self.assertRaises(ValueError):
                    paraboloid(point)

    def test_rosenbrock_requires_two_dimensions(self):
        with self.assertRaises(ValueError):
            rosenbrock([1])
        with self.assertRaises(ValueError):
            get_bounds("rosenbrock", 1)

    def test_invalid_lookup_and_dimensions_are_rejected(self):
        with self.assertRaises(ValueError):
            get_function("unknown")
        with self.assertRaises(TypeError):
            get_bounds("paraboloid", 2.5)
        with self.assertRaises(ValueError):
            get_bounds("paraboloid", 0)

    def test_report_creates_csv_and_both_graphs(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            records = run_objective_tests(
                output,
                runs=1,
                dimensions=2,
                agents=3,
                iterations=2,
                grid_size=8,
            )
            self.assertEqual(len(records), len(FUNCTIONS))
            for filename in (
                "objective_function_results.csv",
                "objective_function_landscapes.png",
                "objective_function_convergence.png",
            ):
                self.assertGreater((output / filename).stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()

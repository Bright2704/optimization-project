import tempfile
import unittest
from pathlib import Path

import numpy as np

from benchmark_report import run_benchmarks
from goa_v2 import GOA_v2, sphere


class GOATests(unittest.TestCase):
    def test_seed_makes_result_reproducible(self):
        arguments = dict(
            fitness_func=sphere,
            n_variables=3,
            lower_bound=[-5] * 3,
            upper_bound=[5] * 3,
            n_grasshoppers=8,
            max_iter=8,
            seed=42,
        )
        first = GOA_v2(**arguments).optimize(verbose=False)
        second = GOA_v2(**arguments).optimize(verbose=False)
        np.testing.assert_allclose(first[0], second[0])
        self.assertEqual(first[1], second[1])

    def test_best_fitness_never_gets_worse(self):
        optimizer = GOA_v2(sphere, 3, [-5] * 3, [5] * 3, 8, 12, seed=7)
        optimizer.optimize(verbose=False)
        self.assertTrue(np.all(np.diff(optimizer.convergence_curve) <= 0))

    def test_report_creates_csv_and_graphs(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            records = run_benchmarks(output, runs=1, dimensions=2, agents=4, iterations=2)
            self.assertEqual(len(records), 3)
            for filename in (
                "benchmark_results.csv",
                "benchmark_convergence.png",
                "benchmark_summary.png",
            ):
                path = output / filename
                self.assertTrue(path.is_file())
                self.assertGreater(path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()

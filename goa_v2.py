"""
Grasshopper Optimisation Algorithm (GOA) - Version 2
=====================================================
Compatibility class for the canonical workshop GOA

Based on: Saremi et al. (2017)
"Grasshopper Optimisation Algorithm: Theory and application"
Advances in Engineering Software 105 (2017) 30-47

Key improvements:
- Bound-scaled coordinate social distances; Euclidean direction vectors
- Retains both c factors; explicit normalization choice documented in docs/methodology.md
"""

import numpy as np
from typing import Callable, Tuple, Optional


class GOA_v2:
    """
    Grasshopper Optimisation Algorithm - Improved Version

    This version uses coordinate/bound normalization, an explicit implementation choice.
    """

    def __init__(
        self,
        fitness_func: Callable,
        n_variables: int,
        lower_bound: np.ndarray,
        upper_bound: np.ndarray,
        n_grasshoppers: int = 30,
        max_iter: int = 500,
        c_max: float = 1.0,
        c_min: float = 0.00001,
        f: float = 0.5,
        l: float = 1.5,
        seed: Optional[int] = None,
    ):
        self.fitness_func = fitness_func
        self.n_variables = n_variables
        self.lower_bound = np.array(lower_bound, dtype=float)
        self.upper_bound = np.array(upper_bound, dtype=float)
        self.n_grasshoppers = n_grasshoppers
        self.max_iter = max_iter
        self.c_max = c_max
        self.c_min = c_min
        self.f = f
        self.l = l
        self.seed = seed
        self.rng = np.random.default_rng(seed)

        if self.n_variables < 1:
            raise ValueError("n_variables must be at least 1")
        if self.n_grasshoppers < 2:
            raise ValueError("n_grasshoppers must be at least 2")
        if self.max_iter < 1:
            raise ValueError("max_iter must be at least 1")
        if self.lower_bound.shape != (self.n_variables,) or self.upper_bound.shape != (self.n_variables,):
            raise ValueError("bounds must contain one value per variable")
        if np.any(self.lower_bound >= self.upper_bound):
            raise ValueError("each lower bound must be smaller than its upper bound")

        self.best_position = None
        self.best_fitness = None
        self.convergence_curve = []

    def _social_force(self, r: float) -> float:
        """
        Social force function s(r) from Eq. (2.3)
        s(r) = f * exp(-r/l) - exp(-r)
        """
        return self.f * np.exp(-r / self.l) - np.exp(-r)

    def _calculate_c(self, iteration: int) -> float:
        """
        Calculate adaptive coefficient c from Eq. (2.8)
        c = c_max - iter * (c_max - c_min) / max_iter
        """
        return self.c_max - iteration * (self.c_max - self.c_min) / self.max_iter

    def _distance(self, a: np.ndarray, b: np.ndarray) -> float:
        """Euclidean distance between two vectors"""
        return np.linalg.norm(a - b)

    def optimize(self, verbose: bool = True) -> Tuple[np.ndarray, float]:
        """Use the canonical workshop GOA; retain the original class interface."""
        from algorithms.core import optimize
        self.result = optimize(
            "goa", self.fitness_func, self.n_variables, self.lower_bound,
            self.upper_bound, self.n_grasshoppers, self.max_iter, self.seed,
            track_positions=True, c_max=self.c_max, c_min=self.c_min,
            f=self.f, l=self.l,
        )
        self.best_position = self.result.best_position
        self.best_fitness = self.result.best_fitness
        self.convergence_curve = self.result.history
        self.positions_history = self.result.positions_history
        self.best_positions_history = self.result.best_positions_history
        self.evaluation_count = self.result.evaluation_count
        if verbose:
            print(f"GOA (documented normalization variant): best={self.best_fitness:.8g}, "
                  f"evaluations={self.evaluation_count}")
        return self.best_position, self.best_fitness


# ============================================================================
# Benchmark Functions (from Paper)
# ============================================================================

def sphere(x: np.ndarray) -> float:
    """F1: Sphere - f(x) = Σ(x_i²), optimum = 0 at origin"""
    return np.sum(x ** 2)


def schwefel_222(x: np.ndarray) -> float:
    """F2: Schwefel 2.22 - f(x) = Σ|x_i| + Π|x_i|, optimum = 0"""
    return np.sum(np.abs(x)) + np.prod(np.abs(x))


def schwefel_12(x: np.ndarray) -> float:
    """F3: Schwefel 1.2 - f(x) = Σ(Σx_j)², optimum = 0"""
    result = 0
    for i in range(len(x)):
        result += np.sum(x[:i+1]) ** 2
    return result


def schwefel_221(x: np.ndarray) -> float:
    """F4: Schwefel 2.21 - f(x) = max|x_i|, optimum = 0"""
    return np.max(np.abs(x))


def rosenbrock(x: np.ndarray) -> float:
    """F5: Rosenbrock - optimum = 0 at (1,1,...,1)"""
    return np.sum(100 * (x[1:] - x[:-1]**2)**2 + (x[:-1] - 1)**2)


def step(x: np.ndarray) -> float:
    """F6: Step - f(x) = Σ(floor(x_i + 0.5))², optimum = 0"""
    return np.sum(np.floor(x + 0.5) ** 2)


def quartic_noise(x: np.ndarray) -> float:
    """F7: Quartic with noise - f(x) = Σ(i*x_i⁴) + random, optimum ≈ 0"""
    n = len(x)
    i = np.arange(1, n + 1)
    return np.sum(i * x**4) + np.random.random()


def rastrigin(x: np.ndarray) -> float:
    """F9: Rastrigin - many local minima, optimum = 0 at origin"""
    n = len(x)
    return 10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))


def ackley(x: np.ndarray) -> float:
    """F10: Ackley - optimum = 0 at origin"""
    n = len(x)
    sum1 = np.sum(x ** 2)
    sum2 = np.sum(np.cos(2 * np.pi * x))
    return -20 * np.exp(-0.2 * np.sqrt(sum1 / n)) - np.exp(sum2 / n) + 20 + np.e


def griewank(x: np.ndarray) -> float:
    """F11: Griewank - optimum = 0 at origin"""
    sum_sq = np.sum(x ** 2) / 4000
    prod_cos = np.prod(np.cos(x / np.sqrt(np.arange(1, len(x) + 1))))
    return sum_sq - prod_cos + 1


# ============================================================================
# Three-bar Truss Design Problem (from Paper Section 4.1)
# ============================================================================

def three_bar_truss(x: np.ndarray) -> float:
    """
    Three-bar truss design problem from paper

    Variables: x = [A1, A2] (cross-sectional areas)
    Minimize: weight = (2*sqrt(2)*x1 + x2) * l
    Subject to: stress constraints

    Parameters: l=100cm, P=2 KN/cm², σ=2 KN/cm²
    Variable range: 0 ≤ x1, x2 ≤ 1

    Optimal solution from paper:
    x1 = 0.788675, x2 = 0.408248
    Optimal weight = 263.8958
    """
    x1, x2 = x[0], x[1]
    l = 100  # cm
    P = 2    # KN/cm²
    sigma = 2  # KN/cm²

    # Objective: minimize weight
    weight = (2 * np.sqrt(2) * x1 + x2) * l

    # Constraints (using death penalty)
    g1 = (np.sqrt(2) * x1 + x2) / (np.sqrt(2) * x1**2 + 2 * x1 * x2) * P - sigma
    g2 = x2 / (np.sqrt(2) * x1**2 + 2 * x1 * x2) * P - sigma
    g3 = 1 / (np.sqrt(2) * x2 + x1) * P - sigma

    # Death penalty for constraint violations
    penalty = 0
    if g1 > 0:
        penalty += 1e10 * g1
    if g2 > 0:
        penalty += 1e10 * g2
    if g3 > 0:
        penalty += 1e10 * g3

    return weight + penalty


# ============================================================================
# Run Paper Benchmarks
# ============================================================================

def run_paper_benchmarks():
    """Run benchmarks as described in the paper"""

    print("\n" + "="*70)
    print("BENCHMARK TESTS (Matching Paper Settings)")
    print("Settings: 30 grasshoppers, 500 iterations")
    print("="*70)

    results = {}

    # Test 1: Sphere Function (F1) - 30 dimensions
    print("\n[F1] Sphere Function (30D)")
    print("True optimum: 0 at origin")

    dim = 30
    goa = GOA_v2(
        fitness_func=sphere,
        n_variables=dim,
        lower_bound=[-100] * dim,
        upper_bound=[100] * dim,
        n_grasshoppers=30,
        max_iter=500
    )
    pos, fit = goa.optimize(verbose=True)
    results['F1_Sphere'] = fit

    # Test 2: Rastrigin (F9) - 30 dimensions
    print("\n[F9] Rastrigin Function (30D)")
    print("True optimum: 0 at origin")

    goa = GOA_v2(
        fitness_func=rastrigin,
        n_variables=dim,
        lower_bound=[-5.12] * dim,
        upper_bound=[5.12] * dim,
        n_grasshoppers=30,
        max_iter=500
    )
    pos, fit = goa.optimize(verbose=True)
    results['F9_Rastrigin'] = fit

    # Test 3: Ackley (F10) - 30 dimensions
    print("\n[F10] Ackley Function (30D)")
    print("True optimum: 0 at origin")

    goa = GOA_v2(
        fitness_func=ackley,
        n_variables=dim,
        lower_bound=[-32] * dim,
        upper_bound=[32] * dim,
        n_grasshoppers=30,
        max_iter=500
    )
    pos, fit = goa.optimize(verbose=True)
    results['F10_Ackley'] = fit

    # Test 4: Three-bar Truss (Real Application)
    print("\n[Real] Three-bar Truss Design Problem")
    print("Paper optimum: weight = 263.8958 at x=[0.7887, 0.4082]")

    goa = GOA_v2(
        fitness_func=three_bar_truss,
        n_variables=2,
        lower_bound=[0.0, 0.0],
        upper_bound=[1.0, 1.0],
        n_grasshoppers=20,
        max_iter=650
    )
    pos, fit = goa.optimize(verbose=True)
    results['ThreeBarTruss'] = {'position': pos, 'weight': fit}

    # Summary
    print("\n" + "="*70)
    print("SUMMARY: Comparison with Paper Results")
    print("="*70)
    print(f"\n{'Function':<20} {'Our Result':<15} {'Paper Result':<15} {'Match?'}")
    print("-"*70)
    print(f"{'F1 Sphere (30D)':<20} {results['F1_Sphere']:<15.4f} {'≈ 0':<15} {'?' if results['F1_Sphere'] > 1 else '✓'}")
    print(f"{'F9 Rastrigin (30D)':<20} {results['F9_Rastrigin']:<15.4f} {'≈ 0':<15} {'?' if results['F9_Rastrigin'] > 1 else '✓'}")
    print(f"{'F10 Ackley (30D)':<20} {results['F10_Ackley']:<15.4f} {'≈ 0':<15} {'?' if results['F10_Ackley'] > 1 else '✓'}")

    truss = results['ThreeBarTruss']
    match_truss = '✓' if abs(truss['weight'] - 263.8958) < 1 else '?'
    print(f"{'Three-bar Truss':<20} {truss['weight']:<15.4f} {'263.8958':<15} {match_truss}")
    print(f"  Position: x1={truss['position'][0]:.6f}, x2={truss['position'][1]:.6f}")
    print(f"  Paper:    x1=0.788675, x2=0.408248")

    return results


# ============================================================================
# Multiple Runs (like Paper's methodology)
# ============================================================================

def run_multiple_trials(n_runs: int = 30):
    """
    Run multiple independent trials like the paper
    Paper uses 30 runs and reports average + std
    """
    print("\n" + "="*70)
    print(f"MULTIPLE TRIALS: {n_runs} independent runs (Paper methodology)")
    print("="*70)

    # Sphere function - 30D
    print("\n[F1] Sphere Function (30D) - Multiple runs")

    dim = 30
    results = []

    for run in range(n_runs):
        goa = GOA_v2(
            fitness_func=sphere,
            n_variables=dim,
            lower_bound=[-100] * dim,
            upper_bound=[100] * dim,
            n_grasshoppers=30,
            max_iter=500
        )
        _, fit = goa.optimize(verbose=False)
        results.append(fit)
        print(f"  Run {run+1:2d}/{n_runs}: {fit:.4f}")

    avg = np.mean(results)
    std = np.std(results)
    best = np.min(results)

    print(f"\n  Average: {avg:.4f}")
    print(f"  Std Dev: {std:.4f}")
    print(f"  Best:    {best:.4f}")
    print(f"\n  Paper reports: avg ≈ 0, std ≈ 0")

    return {'average': avg, 'std': std, 'best': best, 'all': results}


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║     GOA v2 - Paper-Accurate Implementation                        ║
    ║     Comparing results with original paper                         ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Run benchmarks
    results = run_paper_benchmarks()

    # Optional: Run multiple trials (takes longer)
    # run_multiple_trials(n_runs=10)

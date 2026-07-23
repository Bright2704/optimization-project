"""
Grasshopper Optimisation Algorithm (GOA) - Version 2
=====================================================
Improved implementation matching paper more closely

Based on: Saremi et al. (2017)
"Grasshopper Optimisation Algorithm: Theory and application"
Advances in Engineering Software 105 (2017) 30-47

Key improvements:
- Distance normalization per dimension (not Euclidean)
- Matches paper's Eq. (2.7) more precisely
"""

import numpy as np
from typing import Callable, Tuple, List


class GOA_v2:
    """
    Grasshopper Optimisation Algorithm - Improved Version

    This version normalizes distances per-dimension as described in the paper.
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
        l: float = 1.5
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
        """
        Run the GOA optimization algorithm (Paper-accurate version)
        """
        # Initialize population randomly
        grasshoppers = np.random.uniform(
            low=self.lower_bound,
            high=self.upper_bound,
            size=(self.n_grasshoppers, self.n_variables)
        )

        # Calculate initial fitness and find target
        fitness = np.array([self.fitness_func(g) for g in grasshoppers])
        best_idx = np.argmin(fitness)
        target = grasshoppers[best_idx].copy()
        target_fitness = fitness[best_idx]

        self.convergence_curve = [target_fitness]

        if verbose:
            print(f"{'='*60}")
            print(f"GOA v2 (Paper-accurate implementation)")
            print(f"{'='*60}")
            print(f"Variables: {self.n_variables}, Grasshoppers: {self.n_grasshoppers}")
            print(f"Max iterations: {self.max_iter}")
            print(f"Initial best fitness: {target_fitness:.8f}")
            print(f"{'='*60}")

        # Main optimization loop
        for iteration in range(self.max_iter):
            c = self._calculate_c(iteration)

            # Store new positions
            new_positions = np.zeros_like(grasshoppers)

            for i in range(self.n_grasshoppers):
                S = np.zeros(self.n_variables)

                for j in range(self.n_grasshoppers):
                    if i != j:
                        # Calculate distance (Euclidean) for normalization
                        current_dist = self._distance(grasshoppers[i], grasshoppers[j])

                        if current_dist < 1e-10:
                            continue

                        # Process each dimension separately (as per paper Eq. 2.7)
                        for d in range(self.n_variables):
                            # Distance in this dimension
                            dist_d = abs(grasshoppers[j, d] - grasshoppers[i, d])

                            # Normalize distance to [1, 4]
                            # Paper: "normalize the distances between grasshoppers in [1,4]"
                            r_norm = 1 + (dist_d / (self.upper_bound[d] - self.lower_bound[d])) * 3
                            r_norm = np.clip(r_norm, 1, 4)

                            # Social force
                            s_val = self._social_force(r_norm)

                            # Direction (unit vector component)
                            if current_dist > 1e-10:
                                direction = (grasshoppers[j, d] - grasshoppers[i, d]) / current_dist
                            else:
                                direction = 0

                            # Accumulate: c * (ub - lb) / 2 * s * direction
                            S[d] += c * ((self.upper_bound[d] - self.lower_bound[d]) / 2) * s_val * direction

                # Update position: X_i = c * S + Target
                new_positions[i] = c * S + target

                # Boundary check
                new_positions[i] = np.clip(new_positions[i], self.lower_bound, self.upper_bound)

            # Update grasshoppers
            grasshoppers = new_positions.copy()

            # Evaluate fitness and update target
            fitness = np.array([self.fitness_func(g) for g in grasshoppers])
            best_idx = np.argmin(fitness)

            if fitness[best_idx] < target_fitness:
                target = grasshoppers[best_idx].copy()
                target_fitness = fitness[best_idx]

            self.convergence_curve.append(target_fitness)

            if verbose and (iteration + 1) % (self.max_iter // 10) == 0:
                print(f"Iteration {iteration + 1:4d}/{self.max_iter}: "
                      f"Best = {target_fitness:.8f}, c = {c:.6f}")

        self.best_position = target
        self.best_fitness = target_fitness

        if verbose:
            print(f"{'='*60}")
            print(f"Optimization completed!")
            print(f"Best position: {target}")
            print(f"Best fitness:  {target_fitness:.8f}")
            print(f"{'='*60}")

        return target, target_fitness


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

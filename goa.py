"""
Grasshopper Optimisation Algorithm (GOA)
========================================
Implementation based on: Saremi et al. (2017)
"Grasshopper Optimisation Algorithm: Theory and application"
Advances in Engineering Software 105 (2017) 30-47

Author: Implementation for educational purposes
"""

import numpy as np
from typing import Callable, Tuple, List, Optional


class GOA:
    """
    Grasshopper Optimisation Algorithm

    Parameters:
    -----------
    fitness_func : callable
        Objective function to minimize. Takes array of shape (n_variables,) and returns scalar.
    n_variables : int
        Number of decision variables (dimensions)
    lower_bound : array-like
        Lower bounds for each variable
    upper_bound : array-like
        Upper bounds for each variable
    n_grasshoppers : int
        Number of grasshoppers (search agents). Default: 30
    max_iter : int
        Maximum number of iterations. Default: 500
    c_max : float
        Maximum value of c coefficient. Default: 1
    c_min : float
        Minimum value of c coefficient. Default: 0.00001
    f : float
        Intensity of attraction. Default: 0.5
    l : float
        Attractive length scale. Default: 1.5
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
        self.lower_bound = np.array(lower_bound)
        self.upper_bound = np.array(upper_bound)
        self.n_grasshoppers = n_grasshoppers
        self.max_iter = max_iter
        self.c_max = c_max
        self.c_min = c_min
        self.f = f
        self.l = l

        # Results storage
        self.best_position = None
        self.best_fitness = None
        self.convergence_curve = []
        self.population_history = []

    def _social_force(self, r: np.ndarray) -> np.ndarray:
        """
        Social force function s(r) from Eq. (2.3)

        s(r) = f * exp(-r/l) - exp(-r)

        - When r < 2.079: Repulsion (negative value)
        - When r = 2.079: Comfort zone (zero)
        - When r > 2.079: Attraction (positive value)
        """
        return self.f * np.exp(-r / self.l) - np.exp(-r)

    def _calculate_c(self, iteration: int) -> float:
        """
        Calculate adaptive coefficient c from Eq. (2.8)

        c = c_max - iter * (c_max - c_min) / max_iter

        c decreases linearly from c_max to c_min over iterations.
        This balances exploration (high c) and exploitation (low c).
        """
        return self.c_max - iteration * (self.c_max - self.c_min) / self.max_iter

    def _normalize_distance(self, distance: float, min_dist: float, max_dist: float) -> float:
        """
        Normalize distance to range [1, 4] as per paper

        This ensures the social force function works effectively
        regardless of the actual distances between grasshoppers.
        """
        if max_dist - min_dist < 1e-10:
            return 2.5  # Return middle value if all distances are same
        return 1 + 3 * (distance - min_dist) / (max_dist - min_dist)

    def optimize(self, verbose: bool = True) -> Tuple[np.ndarray, float]:
        """
        Run the GOA optimization algorithm

        Returns:
        --------
        best_position : np.ndarray
            The best solution found
        best_fitness : float
            The fitness value of the best solution
        """
        # Step 1: Initialize population randomly
        grasshoppers = np.random.uniform(
            low=self.lower_bound,
            high=self.upper_bound,
            size=(self.n_grasshoppers, self.n_variables)
        )

        # Step 2: Calculate initial fitness and find target
        fitness = np.array([self.fitness_func(g) for g in grasshoppers])
        best_idx = np.argmin(fitness)
        target = grasshoppers[best_idx].copy()
        target_fitness = fitness[best_idx]

        self.convergence_curve = [target_fitness]

        if verbose:
            print(f"{'='*60}")
            print(f"Grasshopper Optimisation Algorithm (GOA)")
            print(f"{'='*60}")
            print(f"Variables: {self.n_variables}, Grasshoppers: {self.n_grasshoppers}")
            print(f"Max iterations: {self.max_iter}")
            print(f"Initial best fitness: {target_fitness:.8f}")
            print(f"{'='*60}")

        # Step 3: Main optimization loop
        for iteration in range(self.max_iter):
            # Calculate adaptive coefficient c (Eq. 2.8)
            c = self._calculate_c(iteration)

            # Calculate all pairwise distances for normalization
            all_distances = []
            for i in range(self.n_grasshoppers):
                for j in range(self.n_grasshoppers):
                    if i != j:
                        dist = np.linalg.norm(grasshoppers[j] - grasshoppers[i])
                        all_distances.append(dist)

            min_dist = min(all_distances) if all_distances else 0
            max_dist = max(all_distances) if all_distances else 1

            # Update each grasshopper's position
            new_positions = np.zeros_like(grasshoppers)

            for i in range(self.n_grasshoppers):
                # Calculate social interaction sum (Eq. 2.7)
                S = np.zeros(self.n_variables)

                for j in range(self.n_grasshoppers):
                    if i != j:
                        # Calculate distance between grasshoppers
                        diff = grasshoppers[j] - grasshoppers[i]
                        distance = np.linalg.norm(diff)

                        if distance < 1e-10:
                            continue

                        # Normalize distance to [1, 4]
                        normalized_dist = self._normalize_distance(distance, min_dist, max_dist)

                        # Calculate social force
                        s_value = self._social_force(normalized_dist)

                        # Calculate unit direction vector
                        direction = diff / distance

                        # Accumulate social interaction
                        # c * (ub - lb) / 2 * s * direction (from Eq. 2.7)
                        S += c * ((self.upper_bound - self.lower_bound) / 2) * s_value * direction

                # Update position: X_i = c * S + Target (Eq. 2.7)
                new_positions[i] = c * S + target

                # Clip to boundaries
                new_positions[i] = np.clip(new_positions[i], self.lower_bound, self.upper_bound)

            # Update grasshoppers positions
            grasshoppers = new_positions.copy()

            # Evaluate fitness and update target
            fitness = np.array([self.fitness_func(g) for g in grasshoppers])
            best_idx = np.argmin(fitness)

            if fitness[best_idx] < target_fitness:
                target = grasshoppers[best_idx].copy()
                target_fitness = fitness[best_idx]

            self.convergence_curve.append(target_fitness)

            # Progress report
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
# Test Functions (Benchmark Functions from Paper)
# ============================================================================

def sphere(x: np.ndarray) -> float:
    """F1: Sphere function - f(x) = Σ(x_i²) - Global minimum at origin = 0"""
    return np.sum(x ** 2)


def rosenbrock(x: np.ndarray) -> float:
    """F5: Rosenbrock function - Global minimum = 0 at (1,1,...,1)"""
    return np.sum(100 * (x[1:] - x[:-1]**2)**2 + (x[:-1] - 1)**2)


def rastrigin(x: np.ndarray) -> float:
    """F9: Rastrigin function - Many local minima, global minimum = 0 at origin"""
    n = len(x)
    return 10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))


def ackley(x: np.ndarray) -> float:
    """F10: Ackley function - Global minimum = 0 at origin"""
    n = len(x)
    sum1 = np.sum(x ** 2)
    sum2 = np.sum(np.cos(2 * np.pi * x))
    return -20 * np.exp(-0.2 * np.sqrt(sum1 / n)) - np.exp(sum2 / n) + 20 + np.e


def griewank(x: np.ndarray) -> float:
    """F11: Griewank function - Global minimum = 0 at origin"""
    sum_sq = np.sum(x ** 2) / 4000
    prod_cos = np.prod(np.cos(x / np.sqrt(np.arange(1, len(x) + 1))))
    return sum_sq - prod_cos + 1


def custom_function(x: np.ndarray) -> float:
    """Custom function from matrix.py: f(x) = x₀² - x₀ + x₁² - 0.5x₁"""
    return x[0]**2 - x[0] + x[1]**2 - 0.5*x[1]


# ============================================================================
# Example Usage and Demonstrations
# ============================================================================

def demo_basic():
    """Basic demonstration with custom function"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Usage - Custom Function")
    print("f(x) = x₀² - x₀ + x₁² - 0.5x₁")
    print("Analytical minimum: x = [0.5, 0.25], f(x) = -0.3125")
    print("="*70)

    goa = GOA(
        fitness_func=custom_function,
        n_variables=2,
        lower_bound=[0, 0],
        upper_bound=[1, 1],
        n_grasshoppers=30,
        max_iter=100
    )

    best_pos, best_fit = goa.optimize()

    print(f"\nAnalytical solution: [0.5, 0.25] = -0.3125")
    print(f"GOA found:           {best_pos} = {best_fit:.8f}")
    print(f"Error: {abs(best_fit - (-0.3125)):.10f}")


def demo_sphere():
    """Demonstration with Sphere function (30 dimensions)"""
    print("\n" + "="*70)
    print("DEMO 2: Sphere Function (30 dimensions)")
    print("f(x) = Σ(x_i²), Global minimum = 0 at origin")
    print("="*70)

    dim = 30
    goa = GOA(
        fitness_func=sphere,
        n_variables=dim,
        lower_bound=[-100] * dim,
        upper_bound=[100] * dim,
        n_grasshoppers=30,
        max_iter=500
    )

    best_pos, best_fit = goa.optimize()
    print(f"\nTrue minimum: 0")
    print(f"GOA found:    {best_fit:.10f}")


def demo_rastrigin():
    """Demonstration with Rastrigin function (multimodal)"""
    print("\n" + "="*70)
    print("DEMO 3: Rastrigin Function (10 dimensions) - Multimodal")
    print("f(x) = 10n + Σ(x_i² - 10cos(2πx_i)), Global minimum = 0")
    print("="*70)

    dim = 10
    goa = GOA(
        fitness_func=rastrigin,
        n_variables=dim,
        lower_bound=[-5.12] * dim,
        upper_bound=[5.12] * dim,
        n_grasshoppers=50,
        max_iter=500
    )

    best_pos, best_fit = goa.optimize()
    print(f"\nTrue minimum: 0")
    print(f"GOA found:    {best_fit:.10f}")


def demo_comparison():
    """Compare GOA with simple random search"""
    print("\n" + "="*70)
    print("DEMO 4: Comparison - GOA vs Random Local Search")
    print("="*70)

    np.random.seed(42)

    # Test on Rastrigin (hard multimodal function)
    dim = 10
    lb = np.array([-5.12] * dim)
    ub = np.array([5.12] * dim)

    # GOA
    print("\nRunning GOA...")
    goa = GOA(
        fitness_func=rastrigin,
        n_variables=dim,
        lower_bound=lb,
        upper_bound=ub,
        n_grasshoppers=30,
        max_iter=200
    )
    goa_pos, goa_fit = goa.optimize(verbose=False)

    # Random Local Search (like matrix.py)
    print("Running Random Local Search...")
    agents = np.random.uniform(lb, ub, (30, dim))
    for _ in range(200):
        for i in range(30):
            new_pos = agents[i] + np.random.normal(0, 0.5, dim)
            new_pos = np.clip(new_pos, lb, ub)
            if rastrigin(new_pos) < rastrigin(agents[i]):
                agents[i] = new_pos

    rls_fitness = [rastrigin(a) for a in agents]
    rls_best = min(rls_fitness)

    print(f"\nResults (lower is better):")
    print(f"  GOA:                  {goa_fit:.6f}")
    print(f"  Random Local Search:  {rls_best:.6f}")
    print(f"  True optimum:         0.000000")

    if goa_fit < rls_best:
        print(f"\n  GOA is better by {rls_best - goa_fit:.6f}")
    else:
        print(f"\n  Random Local Search is better by {goa_fit - rls_best:.6f}")


def plot_convergence(convergence_curve: List[float], title: str = "GOA Convergence"):
    """Plot convergence curve (requires matplotlib)"""
    try:
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 6))
        plt.plot(convergence_curve, 'b-', linewidth=2)
        plt.xlabel('Iteration', fontsize=12)
        plt.ylabel('Best Fitness', fontsize=12)
        plt.title(title, fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.yscale('log')
        plt.tight_layout()
        plt.savefig('goa_convergence.png', dpi=150)
        plt.show()
        print("Convergence plot saved to 'goa_convergence.png'")
    except ImportError:
        print("matplotlib not installed. Skipping plot.")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║     Grasshopper Optimisation Algorithm (GOA) Implementation       ║
    ║     Based on: Saremi et al. (2017)                               ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Run demonstrations
    demo_basic()
    demo_sphere()
    demo_rastrigin()
    demo_comparison()

    # Optional: Plot convergence
    print("\n" + "="*70)
    print("DEMO 5: Convergence Plot")
    print("="*70)

    goa = GOA(
        fitness_func=sphere,
        n_variables=30,
        lower_bound=[-100] * 30,
        upper_bound=[100] * 30,
        n_grasshoppers=30,
        max_iter=200
    )
    goa.optimize(verbose=False)
    plot_convergence(goa.convergence_curve, "GOA Convergence on Sphere Function (30D)")

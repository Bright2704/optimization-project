"""
=============================================================================
    Optimization Algorithms Demo
    ============================
    ทดลองเปรียบเทียบ 3 algorithms กับ 5 objective functions

    Algorithms:
    1. Random Local Search (RLS) - ง่ายที่สุด
    2. Genetic Algorithm (GA)   - วิวัฒนาการทางพันธุกรรม
    3. GOA                      - Grasshopper Optimisation Algorithm

    Objective Functions (from workshop_objective_function.pdf):
    1. Paraboloid (Sphere)  - f(x) = sum(x_i^2), min = 0
    2. Rosenbrock           - Valley-shaped, min = 0 at (1,1,...,1)
    3. Griewank             - Many local minima, min = 0
    4. Schwefel             - Complex landscape
    5. Rastrigin            - Highly multimodal, min = 0
=============================================================================
"""

import numpy as np
import time

# Import algorithms
from algorithms import random_local_search, genetic_algorithm, grasshopper_optimization

# Import objective functions
from utils.objective_functions import (
    paraboloid, rosenbrock, griewank, schwefel, rastrigin,
    BOUNDS, FUNCTIONS
)


def run_single_test(algorithm_func, algorithm_name, objective_func, func_name,
                    n_variables, bounds, max_iter=100, n_agents=30):
    """รัน algorithm หนึ่งครั้งและ return ผลลัพธ์"""

    lb = [bounds[0]] * n_variables
    ub = [bounds[1]] * n_variables

    start_time = time.time()

    if algorithm_name == "RLS":
        pos, fit, hist = algorithm_func(
            fitness_func=objective_func,
            n_variables=n_variables,
            lower_bound=lb,
            upper_bound=ub,
            n_agents=n_agents,
            max_iter=max_iter,
            step_size=0.3
        )
    elif algorithm_name == "GA":
        pos, fit, hist = algorithm_func(
            fitness_func=objective_func,
            n_variables=n_variables,
            lower_bound=lb,
            upper_bound=ub,
            pop_size=n_agents,
            max_iter=max_iter,
            crossover_rate=0.8,
            mutation_rate=0.1
        )
    elif algorithm_name == "GOA":
        pos, fit, hist = algorithm_func(
            fitness_func=objective_func,
            n_variables=n_variables,
            lower_bound=lb,
            upper_bound=ub,
            n_grasshoppers=n_agents,
            max_iter=max_iter
        )

    elapsed = time.time() - start_time

    return {
        'position': pos,
        'fitness': fit,
        'history': hist,
        'time': elapsed
    }


def print_header():
    print()
    print("=" * 70)
    print("     OPTIMIZATION ALGORITHMS COMPARISON")
    print("     เปรียบเทียบ Algorithms กับ Objective Functions")
    print("=" * 70)


def print_result_table(results, algorithms, functions):
    """แสดงตารางผลลัพธ์"""

    print()
    print("-" * 70)
    print(f"{'Function':<15} {'RLS':<18} {'GA':<18} {'GOA':<18}")
    print("-" * 70)

    for func_name in functions:
        row = f"{func_name:<15}"
        for algo_name in algorithms:
            fit = results[algo_name][func_name]['fitness']
            row += f" {fit:<17.6f}"
        print(row)

    print("-" * 70)


def demo_basic():
    """Demo พื้นฐาน: ทดสอบกับ Sphere function"""

    print("\n" + "=" * 70)
    print("  DEMO 1: Basic Test - Sphere Function (2D)")
    print("  f(x) = x1^2 + x2^2, minimum = 0 at [0, 0]")
    print("=" * 70)

    def sphere(x):
        return np.sum(np.array(x)**2)

    n_var = 2
    lb = [-5, -5]
    ub = [5, 5]
    max_iter = 50
    n_agents = 20

    print(f"\nSettings: {n_var}D, {n_agents} agents, {max_iter} iterations")
    print("-" * 50)

    # Test RLS
    pos, fit, _ = random_local_search(sphere, n_var, lb, ub, n_agents, max_iter, seed=42)
    print(f"RLS: fitness = {fit:.8f}, position = [{pos[0]:.4f}, {pos[1]:.4f}]")

    # Test GA
    pos, fit, _ = genetic_algorithm(sphere, n_var, lb, ub, n_agents, max_iter, seed=42)
    print(f"GA:  fitness = {fit:.8f}, position = [{pos[0]:.4f}, {pos[1]:.4f}]")

    # Test GOA
    pos, fit, _ = grasshopper_optimization(sphere, n_var, lb, ub, n_agents, max_iter, seed=42)
    print(f"GOA: fitness = {fit:.8f}, position = [{pos[0]:.4f}, {pos[1]:.4f}]")

    print("-" * 50)
    print("True minimum: 0 at [0, 0]")


def demo_all_functions():
    """Demo: ทดสอบกับทุก objective functions"""

    print("\n" + "=" * 70)
    print("  DEMO 2: All Objective Functions (5D)")
    print("=" * 70)

    # Settings
    n_variables = 5
    max_iter = 100
    n_agents = 30

    # Algorithms
    algorithms = {
        'RLS': random_local_search,
        'GA': genetic_algorithm,
        'GOA': grasshopper_optimization
    }

    # Objective functions (skip rosenbrock as it needs n>=2)
    test_functions = {
        'Paraboloid': (paraboloid, BOUNDS['paraboloid']),
        'Rosenbrock': (rosenbrock, BOUNDS['rosenbrock']),
        'Griewank': (griewank, BOUNDS['griewank']),
        'Rastrigin': (rastrigin, BOUNDS['rastrigin']),
    }

    print(f"\nSettings: {n_variables}D, {n_agents} agents, {max_iter} iterations")

    # Run all tests
    results = {algo: {} for algo in algorithms}

    for func_name, (func, bounds) in test_functions.items():
        print(f"\nTesting {func_name}...")

        for algo_name, algo_func in algorithms.items():
            result = run_single_test(
                algo_func, algo_name, func, func_name,
                n_variables, bounds, max_iter, n_agents
            )
            results[algo_name][func_name] = result

    # Print results
    print_result_table(results, list(algorithms.keys()), list(test_functions.keys()))

    # Print winner for each function
    print("\nWinner for each function (lowest fitness):")
    for func_name in test_functions:
        best_algo = min(algorithms.keys(), key=lambda a: results[a][func_name]['fitness'])
        best_fit = results[best_algo][func_name]['fitness']
        print(f"  {func_name:<15}: {best_algo} ({best_fit:.6f})")


def demo_comparison_30d():
    """Demo: เปรียบเทียบใน 30 มิติ"""

    print("\n" + "=" * 70)
    print("  DEMO 3: High-Dimensional Test (30D) - Sphere Function")
    print("  ทดสอบความสามารถในการค้นหาใน search space ขนาดใหญ่")
    print("=" * 70)

    def sphere(x):
        return np.sum(np.array(x)**2)

    n_var = 30
    bounds = BOUNDS['paraboloid']
    lb = [bounds[0]] * n_var
    ub = [bounds[1]] * n_var
    max_iter = 200
    n_agents = 30

    print(f"\nSettings: {n_var}D, {n_agents} agents, {max_iter} iterations")
    print("-" * 50)

    # Test each algorithm
    for name, func in [('RLS', random_local_search),
                       ('GA', genetic_algorithm),
                       ('GOA', grasshopper_optimization)]:

        start = time.time()

        if name == 'RLS':
            _, fit, _ = func(sphere, n_var, lb, ub, n_agents, max_iter, step_size=0.5)
        elif name == 'GA':
            _, fit, _ = func(sphere, n_var, lb, ub, n_agents, max_iter)
        else:
            _, fit, _ = func(sphere, n_var, lb, ub, n_agents, max_iter)

        elapsed = time.time() - start
        print(f"{name:>5}: fitness = {fit:>12.6f}  (time: {elapsed:.3f}s)")

    print("-" * 50)
    print("True minimum: 0")


def demo_convergence():
    """Demo: แสดง convergence behavior"""

    print("\n" + "=" * 70)
    print("  DEMO 4: Convergence Behavior")
    print("  ดูว่า algorithm ค้นหาคำตอบเร็วแค่ไหน")
    print("=" * 70)

    def rastrigin(x):
        x = np.array(x)
        n = len(x)
        return 10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))

    n_var = 10
    bounds = BOUNDS['rastrigin']
    lb = [bounds[0]] * n_var
    ub = [bounds[1]] * n_var
    max_iter = 100
    n_agents = 30

    print(f"\nFunction: Rastrigin ({n_var}D), True minimum = 0")
    print("-" * 50)

    results = {}

    # RLS
    _, fit, hist = random_local_search(rastrigin, n_var, lb, ub, n_agents, max_iter, seed=42)
    results['RLS'] = hist

    # GA
    _, fit, hist = genetic_algorithm(rastrigin, n_var, lb, ub, n_agents, max_iter, seed=42)
    results['GA'] = hist

    # GOA
    _, fit, hist = grasshopper_optimization(rastrigin, n_var, lb, ub, n_agents, max_iter, seed=42)
    results['GOA'] = hist

    # Show convergence at different iterations
    checkpoints = [0, 10, 25, 50, 75, 100]
    print(f"\n{'Iter':<8} {'RLS':<15} {'GA':<15} {'GOA':<15}")
    print("-" * 50)

    for cp in checkpoints:
        if cp < len(results['RLS']):
            rls_val = results['RLS'][cp]
            ga_val = results['GA'][cp]
            goa_val = results['GOA'][cp]
            print(f"{cp:<8} {rls_val:<15.4f} {ga_val:<15.4f} {goa_val:<15.4f}")


def demo_custom_function():
    """Demo: ทดสอบกับ custom function"""

    print("\n" + "=" * 70)
    print("  DEMO 5: Custom Function")
    print("  f(x) = x1^2 - x1 + x2^2 - 0.5*x2")
    print("  Analytical minimum: [-0.3125] at [0.5, 0.25]")
    print("=" * 70)

    def custom_func(x):
        return x[0]**2 - x[0] + x[1]**2 - 0.5*x[1]

    n_var = 2
    lb = [0, 0]
    ub = [1, 1]
    max_iter = 100
    n_agents = 30

    print(f"\nSettings: {n_var}D, bounds=[0,1], {max_iter} iterations")
    print("-" * 50)

    # Test each algorithm
    for name, func in [('RLS', random_local_search),
                       ('GA', genetic_algorithm),
                       ('GOA', grasshopper_optimization)]:

        if name == 'RLS':
            pos, fit, _ = func(custom_func, n_var, lb, ub, n_agents, max_iter, step_size=0.1)
        elif name == 'GA':
            pos, fit, _ = func(custom_func, n_var, lb, ub, n_agents, max_iter)
        else:
            pos, fit, _ = func(custom_func, n_var, lb, ub, n_agents, max_iter)

        print(f"{name:>5}: fitness = {fit:>10.6f}  position = [{pos[0]:.4f}, {pos[1]:.4f}]")

    print("-" * 50)
    print(f"True:  fitness = {-0.3125:>10.6f}  position = [0.5000, 0.2500]")


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print_header()

    # เลือก demo ที่ต้องการรัน
    print("\nSelect demo to run:")
    print("  1. Basic Test (2D Sphere)")
    print("  2. All Objective Functions (5D)")
    print("  3. High-Dimensional (30D)")
    print("  4. Convergence Behavior")
    print("  5. Custom Function")
    print("  6. Run ALL demos")
    print()

    try:
        choice = input("Enter choice (1-6) [default=6]: ").strip()
        if choice == '' or choice == '6':
            demo_basic()
            demo_all_functions()
            demo_comparison_30d()
            demo_convergence()
            demo_custom_function()
        elif choice == '1':
            demo_basic()
        elif choice == '2':
            demo_all_functions()
        elif choice == '3':
            demo_comparison_30d()
        elif choice == '4':
            demo_convergence()
        elif choice == '5':
            demo_custom_function()
        else:
            print("Invalid choice. Running all demos...")
            demo_basic()
            demo_all_functions()
            demo_comparison_30d()
            demo_convergence()
            demo_custom_function()

    except EOFError:
        # Run all demos if no input (e.g., in non-interactive mode)
        demo_basic()
        demo_all_functions()
        demo_comparison_30d()
        demo_convergence()
        demo_custom_function()

    print("\n" + "=" * 70)
    print("  Demo completed!")
    print("=" * 70)

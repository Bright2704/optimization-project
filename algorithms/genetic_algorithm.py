"""Real-number GA compatibility interface; see algorithms.core."""
from .core import optimize


def genetic_algorithm(fitness_func, n_variables, lower_bound, upper_bound,
                      pop_size=30, max_iter=100, crossover_rate=0.8,
                      mutation_rate=0.1, seed=None, track_positions=False,
                      return_details=False):
    result = optimize("ga", fitness_func, n_variables, lower_bound, upper_bound,
                      pop_size, max_iter, seed, track_positions,
                      crossover_rate=crossover_rate, mutation_rate=mutation_rate)
    return result if return_details else result.legacy(track_positions)

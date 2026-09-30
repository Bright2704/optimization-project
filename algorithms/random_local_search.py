"""Parallel random local searches; includes initial fitness at iteration 0."""
from .core import optimize


def random_local_search(fitness_func, n_variables, lower_bound, upper_bound,
                        n_agents=30, max_iter=100, step_size=0.1, seed=None,
                        track_positions=False, return_details=False):
    result = optimize("rls", fitness_func, n_variables, lower_bound, upper_bound,
                      n_agents, max_iter, seed, track_positions, step_size=step_size)
    return result if return_details else result.legacy(track_positions)

"""GOA compatibility interface; canonical implementation: algorithms.core."""
from .core import optimize


def grasshopper_optimization(fitness_func, n_variables, lower_bound, upper_bound,
                            n_grasshoppers=30, max_iter=100, c_max=1.0,
                            c_min=0.00001, f=0.5, l=1.5, seed=None,
                            track_positions=False, return_details=False):
    result = optimize("goa", fitness_func, n_variables, lower_bound, upper_bound,
                      n_grasshoppers, max_iter, seed, track_positions,
                      c_max=c_max, c_min=c_min, f=f, l=l)
    return result if return_details else result.legacy(track_positions)

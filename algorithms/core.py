"""Canonical workshop optimizers. Every trace includes states 0 through T.

GOA uses Eq. 2.7/2.8 of Saremi et al. (2017), with an explicitly chosen
coordinate/bound normalization to [1, 4]. See docs/methodology.md.
Objectives must be deterministic; cached fitness avoids redundant evaluations.
"""
from dataclasses import dataclass
from numbers import Integral
from time import perf_counter

import numpy as np


@dataclass
class OptimizationResult:
    best_position: np.ndarray
    best_fitness: float
    history: list
    positions_history: list
    best_positions_history: list
    population_fitness_history: list
    evaluations_history: list
    evaluation_count: int
    runtime_seconds: float

    def legacy(self, track_positions=False):
        values = (self.best_position, self.best_fitness, self.history)
        return values + (self.positions_history,) if track_positions else values


def goa_step(positions, target, lb, ub, c, f=0.5, l=1.5):
    """Synchronous update; vectorization preserves pairwise Eq. 2.7 sums.

    r_ijd = 1 + 3 |x_jd - x_id| / (ub_d - lb_d).
    Direction uses the Euclidean distance. Coincident pairs contribute zero.
    Both occurrences of c and the bound width / 2 are retained.
    """
    diff = positions[None, :, :] - positions[:, None, :]
    distance = np.linalg.norm(diff, axis=2)
    direction = np.divide(diff, distance[:, :, None], out=np.zeros_like(diff),
                          where=distance[:, :, None] > 1e-10)
    r = np.clip(1 + 3 * np.abs(diff) / (ub - lb), 1, 4)
    social = f * np.exp(-r / l) - np.exp(-r)
    force = np.sum(c * (ub - lb) / 2 * social * direction, axis=1)
    return np.clip(c * force + target, lb, ub)


def optimize(algorithm, fitness_func, n_variables, lower_bound, upper_bound,
             n_agents=30, max_iter=100, seed=None, track_positions=True,
             c_max=1.0, c_min=1e-5, f=0.5, l=1.5,
             crossover_rate=0.8, mutation_rate=0.1, step_size=0.3):
    """Return best among *all evaluated points*, including rejected candidates.

    GA: real arithmetic crossover, roulette selection, Gaussian individual
    mutation (sigma = 0.1 bound width), no population elitism, best archive.
    RLS: N independent local searches, Gaussian proposals, accept <= current.
    Runtime includes initialization, search and trace storage, excludes plots.
    """
    for name, value, minimum in (("n_variables", n_variables, 1),
                                 ("n_agents", n_agents, 2), ("max_iter", max_iter, 0)):
        if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    lb, ub = np.asarray(lower_bound, float), np.asarray(upper_bound, float)
    if lb.shape != (n_variables,) or ub.shape != lb.shape:
        raise ValueError("bounds must contain one value per dimension")
    if not np.all(np.isfinite([lb, ub])) or np.any(lb >= ub):
        raise ValueError("bounds must be finite and strictly ordered")
    if algorithm not in {"goa", "ga", "rls"}:
        raise ValueError("unknown algorithm")
    if not np.all(np.isfinite([c_max, c_min, f, l, step_size,
                               crossover_rate, mutation_rate])):
        raise ValueError("parameters must be finite")
    if not 0 < c_min <= c_max or l <= 0 or f < 0 or step_size <= 0:
        raise ValueError("invalid GOA or RLS parameters")
    if not 0 <= crossover_rate <= 1 or not 0 <= mutation_rate <= 1:
        raise ValueError("rates must lie in [0,1]")
    start = perf_counter()
    rng = np.random.default_rng(seed)
    evaluations = 0

    def evaluate(points):
        nonlocal evaluations
        values = []
        for point in points:
            values.append(float(fitness_func(point)))
            evaluations += 1  # actual scalar objective calls
        values = np.asarray(values)
        if not np.all(np.isfinite(values)):
            raise ValueError("objective returned a non-finite value")
        return values

    positions = rng.uniform(lb, ub, (n_agents, n_variables))
    fitness = evaluate(positions)
    idx = np.argmin(fitness)
    best, best_fit = positions[idx].copy(), float(fitness[idx])
    history, frames, best_positions, population_values, evals = [], [], [], [], []

    def record():
        history.append(best_fit)
        best_positions.append(best.copy())
        population_values.append(fitness.copy())
        evals.append(evaluations)
        if track_positions:
            frames.append(positions.copy())

    record()  # iteration 0
    for iteration in range(1, max_iter + 1):
        if algorithm == "goa":
            c = c_max - iteration * (c_max - c_min) / max_iter
            candidates = goa_step(positions, best, lb, ub, c, f, l)
        elif algorithm == "rls":
            candidates = np.clip(positions + rng.normal(0, step_size, positions.shape), lb, ub)
        else:
            weights = fitness.max() - fitness + 1e-10
            parents = positions[rng.choice(n_agents, n_agents, p=weights / weights.sum())]
            children = []
            for i in range(0, n_agents, 2):
                a, b = parents[i], parents[min(i + 1, n_agents - 1)]
                if rng.random() < crossover_rate:
                    alpha = rng.random()
                    pair = (alpha * a + (1-alpha) * b, (1-alpha) * a + alpha * b)
                else:
                    pair = (a.copy(), b.copy())
                children.extend(pair)
            candidates = np.asarray(children[:n_agents])
            for i in range(n_agents):
                if rng.random() < mutation_rate:
                    candidates[i] += rng.normal(0, 0.1 * (ub-lb), n_variables)
            candidates = np.clip(candidates, lb, ub)
        candidate_fitness = evaluate(candidates)
        idx = np.argmin(candidate_fitness)
        if candidate_fitness[idx] < best_fit:
            best, best_fit = candidates[idx].copy(), float(candidate_fitness[idx])
        if algorithm == "rls":
            accept = candidate_fitness <= fitness
            positions[accept], fitness[accept] = candidates[accept], candidate_fitness[accept]
        else:
            positions, fitness = candidates, candidate_fitness
        record()
    return OptimizationResult(best, best_fit, history, frames, best_positions,
                              population_values, evals, evaluations, perf_counter()-start)

"""Test the workshop objective functions with GOA and generate graph reports."""

from __future__ import annotations

import argparse
import csv
import os
import tempfile
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "goa-matplotlib")
)

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from goa_v2 import GOA_v2
from utils.objective_functions import BOUNDS, FUNCTIONS


MINIMIZERS = {
    "paraboloid": 0.0,
    "rosenbrock": 1.0,
    "griewank": 0.0,
    "schwefel": 420.9687,
    "rastrigin": 0.0,
}


def run_objective_tests(
    output_dir: Path,
    runs: int = 3,
    dimensions: int = 2,
    agents: int = 25,
    iterations: int = 150,
    seed: int = 2026,
    grid_size: int = 160,
) -> list[dict]:
    """Optimize all workshop functions and save CSV plus two graph reports."""
    if min(runs, dimensions, agents, iterations, grid_size) < 1:
        raise ValueError("all numeric settings must be positive")
    if dimensions < 2:
        raise ValueError("dimensions must be at least 2")
    if agents < 2:
        raise ValueError("agents must be at least 2")

    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []

    for function_index, (name, function) in enumerate(FUNCTIONS.items()):
        lower, upper = BOUNDS[name]
        for run_index in range(runs):
            run_seed = seed + function_index * 10_000 + run_index
            optimizer = GOA_v2(
                fitness_func=function,
                n_variables=dimensions,
                lower_bound=[lower] * dimensions,
                upper_bound=[upper] * dimensions,
                n_grasshoppers=agents,
                max_iter=iterations,
                seed=run_seed,
            )
            position, fitness = optimizer.optimize(verbose=False)
            records.append(
                {
                    "function": name,
                    "run": run_index + 1,
                    "seed": run_seed,
                    "best_fitness": float(fitness),
                    "best_position": position.copy(),
                    "convergence": np.asarray(optimizer.convergence_curve),
                }
            )
            print(
                f"{name:<11} run {run_index + 1}/{runs}: "
                f"fitness={fitness:.8g}, position={np.array2string(position, precision=4)}"
            )

    _write_results(records, output_dir / "objective_function_results.csv")
    _plot_landscapes(output_dir / "objective_function_landscapes.png", grid_size)
    _plot_convergence(records, output_dir / "objective_function_convergence.png")
    return records


def _known_point(name: str, dimensions: int) -> np.ndarray:
    return np.full(dimensions, MINIMIZERS[name], dtype=float)


def _known_fitness(name: str, dimensions: int) -> float:
    return FUNCTIONS[name](_known_point(name, dimensions))


def _write_results(records: list[dict], path: Path) -> None:
    fields = ("function", "run", "seed", "best_fitness", "best_position")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "function": record["function"],
                    "run": record["run"],
                    "seed": record["seed"],
                    "best_fitness": record["best_fitness"],
                    "best_position": np.array2string(
                        record["best_position"], separator=" ", max_line_width=10_000
                    ),
                }
            )


def _plot_landscapes(path: Path, grid_size: int) -> None:
    figure, axes = plt.subplots(2, 3, figsize=(16, 10), constrained_layout=True)
    for axis, (name, function) in zip(axes.flat, FUNCTIONS.items()):
        lower, upper = BOUNDS[name]
        coordinates = np.linspace(lower, upper, grid_size)
        xx, yy = np.meshgrid(coordinates, coordinates)
        zz = np.fromiter(
            (function((x, y)) for x, y in zip(xx.ravel(), yy.ravel())),
            dtype=float,
            count=xx.size,
        ).reshape(xx.shape)

        # log1p makes narrow minima visible without changing optimizer inputs.
        display_values = np.log1p(np.maximum(zz - np.min(zz), 0.0))
        contour = axis.contourf(xx, yy, display_values, levels=35, cmap="viridis")
        minimizer = MINIMIZERS[name]
        axis.scatter(
            minimizer, minimizer, marker="*", s=130, c="red", edgecolors="white"
        )
        axis.set(title=name.capitalize(), xlabel="$x_1$", ylabel="$x_2$")
        figure.colorbar(contour, ax=axis, label="log(1 + f(x) - grid min)")

    axes.flat[-1].axis("off")
    figure.suptitle("Workshop objective functions in 2D", fontsize=17)
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _plot_convergence(records: list[dict], path: Path) -> None:
    figure, axes = plt.subplots(2, 3, figsize=(16, 9), constrained_layout=True)
    for axis, name in zip(axes.flat, FUNCTIONS):
        selected = [record for record in records if record["function"] == name]
        curves = np.stack([record["convergence"] for record in selected])
        known_fitness = _known_fitness(name, selected[0]["best_position"].size)
        gaps = np.maximum(curves - known_fitness, np.finfo(float).tiny)
        x = np.arange(curves.shape[1])
        for gap in gaps:
            axis.plot(x, gap, alpha=0.25, linewidth=1)
        axis.plot(x, gaps.mean(axis=0), color="black", linewidth=2, label="Mean gap")
        axis.set_yscale("log")
        axis.set(
            title=name.capitalize(),
            xlabel="Iteration",
            ylabel="Best fitness - known optimum",
        )
        axis.grid(True, alpha=0.25)
        axis.legend(fontsize=8)

    axes.flat[-1].axis("off")
    figure.suptitle("GOA optimality-gap convergence", fontsize=17)
    figure.savefig(path, dpi=160)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--dimensions", type=int, default=2)
    parser.add_argument("--agents", type=int, default=25)
    parser.add_argument("--iterations", type=int, default=150)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--grid-size", type=int, default=160)
    args = parser.parse_args()
    records = run_objective_tests(
        args.output_dir,
        args.runs,
        args.dimensions,
        args.agents,
        args.iterations,
        args.seed,
        args.grid_size,
    )
    print(f"\nSaved {len(records)} optimization runs to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()

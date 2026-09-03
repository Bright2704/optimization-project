"""Run reproducible GOA benchmarks and save their results as graphs and CSV."""

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

from goa_v2 import GOA_v2, ackley, rastrigin, sphere


BENCHMARKS = {
    "Sphere": (sphere, -100.0, 100.0),
    "Rastrigin": (rastrigin, -5.12, 5.12),
    "Ackley": (ackley, -32.0, 32.0),
}


def run_benchmarks(
    output_dir: Path,
    runs: int = 3,
    dimensions: int = 10,
    agents: int = 20,
    iterations: int = 100,
    base_seed: int = 2026,
) -> list[dict]:
    """Execute every benchmark and return one record per independent run."""
    if min(runs, dimensions, agents, iterations) < 1:
        raise ValueError("runs, dimensions, agents and iterations must be positive")
    if agents < 2:
        raise ValueError("agents must be at least 2")

    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []

    for benchmark_index, (name, (function, lower, upper)) in enumerate(
        BENCHMARKS.items()
    ):
        for run_index in range(runs):
            seed = base_seed + benchmark_index * 10_000 + run_index
            optimizer = GOA_v2(
                fitness_func=function,
                n_variables=dimensions,
                lower_bound=[lower] * dimensions,
                upper_bound=[upper] * dimensions,
                n_grasshoppers=agents,
                max_iter=iterations,
                seed=seed,
            )
            position, fitness = optimizer.optimize(verbose=False)
            records.append(
                {
                    "benchmark": name,
                    "run": run_index + 1,
                    "seed": seed,
                    "best_fitness": float(fitness),
                    "best_position_norm": float(np.linalg.norm(position)),
                    "convergence": np.asarray(optimizer.convergence_curve, dtype=float),
                }
            )
            print(f"{name:<10} run {run_index + 1}/{runs}: {fitness:.8g}")

    _write_csv(records, output_dir / "benchmark_results.csv")
    _plot_convergence(records, output_dir / "benchmark_convergence.png")
    _plot_summary(records, output_dir / "benchmark_summary.png")
    return records


def _write_csv(records: list[dict], path: Path) -> None:
    fields = ("benchmark", "run", "seed", "best_fitness", "best_position_norm")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: record[key] for key in fields} for record in records)


def _plot_convergence(records: list[dict], path: Path) -> None:
    figure, axis = plt.subplots(figsize=(10, 6))
    for name in BENCHMARKS:
        curves = np.stack([r["convergence"] for r in records if r["benchmark"] == name])
        mean = curves.mean(axis=0)
        std = curves.std(axis=0)
        x = np.arange(mean.size)
        safe_mean = np.maximum(mean, np.finfo(float).tiny)
        axis.plot(x, safe_mean, linewidth=2, label=name)
        axis.fill_between(
            x,
            np.maximum(mean - std, np.finfo(float).tiny),
            np.maximum(mean + std, np.finfo(float).tiny),
            alpha=0.16,
        )
    axis.set(
        title="GOA benchmark convergence",
        xlabel="Iteration",
        ylabel="Best fitness (mean ± SD)",
    )
    axis.set_yscale("log")
    axis.grid(True, which="both", alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _plot_summary(records: list[dict], path: Path) -> None:
    names = list(BENCHMARKS)
    samples = [
        [r["best_fitness"] for r in records if r["benchmark"] == name] for name in names
    ]
    figure, axis = plt.subplots(figsize=(9, 5.5))
    axis.boxplot(samples, tick_labels=names, showmeans=True)
    axis.set(
        title="Final fitness across independent runs",
        ylabel="Best fitness (lower is better)",
    )
    axis.set_yscale("log")
    axis.grid(True, axis="y", which="both", alpha=0.25)
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--dimensions", type=int, default=10)
    parser.add_argument("--agents", type=int, default=20)
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    records = run_benchmarks(
        args.output_dir,
        args.runs,
        args.dimensions,
        args.agents,
        args.iterations,
        args.seed,
    )
    print(f"\nSaved {len(records)} runs to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()

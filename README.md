# GOA Optimization Workshop — Aj. Eckart

12-slide, 12-minute presentation backed by 180 measured runs comparing GOA, GA and parallel RLS on Sphere and Rosenbrock. See [methodology](docs/methodology.md) for the equations, normalization choice, fairness and limitations. The workshop uses one canonical implementation (`algorithms/core.py`) across experiments, web, animation and snapshots.

## Install

Python 3.11+ recommended (this export was tested on Python 3.14). Use an isolated environment:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-workshop.txt
```

Alternatively, if using uv:

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements-workshop.txt
```

The pre-existing requirements.txt is preserved. Workshop dependencies are recorded separately in requirements-workshop.txt; exact tested versions are recorded in requirements-workshop.lock.txt. FFmpeg enables MP4 export; LibreOffice enables PDF conversion; Poppler (`pdftoppm`, `pdftotext`, `pdfinfo`) enables PDF rendering/audit. These are external system packages. For the slide font install **IBM Plex Sans Thai**, or a compatible Thai font and adjust `workshop/presentation.py`. These tools were available and used for the delivered exports. GIF/PPTX remain available if optional system exporters are unavailable.

## Test and run the web app

```bash
.venv/bin/python -m pytest -q
.venv/bin/python app.py
```

Open http://127.0.0.1:8080. If that port is occupied, use `.venv/bin/python app.py --port 8091` and `.venv/bin/python scripts/browser_check.py --url http://127.0.0.1:8091` (the delivered browser audit used 8091). Select function/algorithm, set seed, run, animate, play/pause, step or seek. Default presentation setup: GOA, 30 agents, 100 iterations, seed 424242. Plotly is served locally from the Python dependency, so no CDN or internet is needed during presentation. API responses retain full precision; the green star is the known optimum and orange marker is current best-so-far. Compare All is a **single demonstration run** per method, not the 30-run statistics.

## Reproduce all deliverables

```bash
.venv/bin/python -m workshop all
```

This writes a fresh complete experiment and updates plots, examples, animations, slide deck, PDF, Thai script/Q&A and verification report. Rebuilding the statistical experiment replaces files inside results/workshop; the existing legacy results at results/ are preserved. Numerical outcomes are reproducible with the recorded seeds and environment; wall-clock runtime and generated-file metadata can vary.

Individual stages (run in this order for a new export):

```bash
.venv/bin/python -m workshop experiments
.venv/bin/python -m workshop plots
.venv/bin/python -m workshop animations
.venv/bin/python -m workshop presentation
.venv/bin/python -m workshop verify
```

`experiments` also creates the two preselected illustration traces. `plots` creates all statistical charts and snapshots. `animations` exports all illustration frames to GIF and MP4. `presentation` uses the existing raw summaries and plots, without rerunning optimization. `verify` inspects raw runs, summaries, image/vector exports, actual video/GIF frames, slide/PDF text and timing. Browser validation is separate:

```bash
.venv/bin/python scripts/browser_check.py
```

Keep the app running for that command. Install a browser for Playwright if none is available: `.venv/bin/python -m playwright install chromium`. Or set `WORKSHOP_CHROMIUM` to an existing Chromium executable. Browser evidence is saved in docs/verification/browser.json and screenshots in docs/verification/. It checks all six method/function combinations, play/pause/seek, marker meanings, display values and offline loading.

Quick experiments can use `--runs 2 --agents 8 --iterations 10 --output-dir /tmp/goa-smoke`; presentation generation deliberately requires the specified full setup, so a smoke test cannot accidentally replace the workshop deck.

## Deliverables

- [PPTX](presentation/GOA_Optimization_Workshop.pptx), [PDF](presentation/GOA_Optimization_Workshop.pdf)
- [Thai script and timing](presentation/script_th.md), [14 Q&A answers](presentation/qa_th.md)
- [Measured conclusions and complete table](results/workshop/RESULTS.md)
- `results/workshop/config.json`, `provenance.json`: parameters, schedule, environment, source hashes
- `results/workshop/runs.csv`, `runs.json`, `summary.csv`, `summary.json`: all 180 runs and aggregate results
- `results/workshop/runs/`: each run's config/results JSON, per-iteration CSV, compressed NPZ with agent positions, population fitness, best positions/fitness and actual evaluations
- `results/workshop/plots/`: mean ± sample SD, median, final boxplot, optimality gap, evaluation-axis convergence, population mean and summary tables; high-resolution PNG and SVG for both functions
- `results/workshop/examples/`: single illustrative GOA traces, seed 424242, excluded from statistical aggregates
- `results/workshop/animations/`: Sphere/Rosenbrock GIF + MP4 and export manifest
- `results/workshop/snapshots/`: 0,25,50,75,100, full strip and slide strip, PNG/SVG; individual images include full bounds + fixed zoom
- `presentation/rendered/`: actual PDF page renders and contact sheet
- `docs/verification/`: scientific/export verification, pytest output and real-browser evidence
- [Completion audit](docs/completion_audit.md)

Keep presentation/ and results/workshop/ together when copying the deck; slide video hyperlinks use relative paths. PDF contains static fallback images; open GIF/MP4 externally for motion. The allocated speaking time is 12 minutes, excluding Q&A; rehearse with the actual presenter to stay below 15 minutes.

## Existing entry points

`animation_simple.py`, `snapshots_simple.py`, `goa_v2.py`, `benchmark_report.py`, `objective_function_report.py` and algorithm function signatures remain usable, backed by the canonical GOA where applicable. The legacy reports have their own benchmarks/bounds/defaults and are not the workshop's 180-run comparison. `goa.py`, `goa_equations.py`, ALGORITHM_GUIDE.md and PROJECT_DOCUMENTATION.md are historical educational material; the current methodology/README define workshop behavior.

The workshop work is on `workshop/goa-presentation`. The user subsequently authorized committing and pushing this branch; merging and deployment are separate actions. Virtual environments, caches, browser runtime logs and dependencies are excluded from git.

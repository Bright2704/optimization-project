# Completion audit — 30 September 2026

The original attached request was audited against the current files and actual executions. Work is on `workshop/goa-presentation`, based on commit `2c633fa`; origin is `git@github.com:Bright2704/optimization-project.git`. No AGENTS.md or AGENT.md was found in the project or ancestor directories. Existing untracked requirements.txt and legacy objective-function result files were preserved. The user subsequently authorized committing and pushing the workshop branch, including its GUI demonstration artifacts. The pre-existing untracked files remain outside this commit. No merge or deployment is included. Local Flask serving for browser validation is not a production deployment.

| Requirement | Current authoritative evidence | Result |
|---|---|---|
| Inspect algorithms, GOA_v2, app, JS, simple exports, both reports, old tests | All inspected; changed sources in git diff; methodology records the old/new distinctions | Verified |
| Correct Sphere/Rosenbrock formulas and optimum | utils/objective_functions.py; original formula tests; six optimizer/API cases in tests_workshop.py; raw trace audit | Verified |
| Separate known optimum, best-so-far, current agents | API known_optimum and archive history; JS traces; browser screenshots and exact frame-25 comparisons; static/GIF/MP4 markers | Verified |
| Single inspected GOA for statistics, web, animation, snapshots | algorithms/core.py; GOA_v2 and function wrappers; simple-wrapper numerical equivalence test | Verified |
| Explain equations and deviations from paper | docs/methodology.md cites inspected Eq.2.7/2.8 and explicit coordinate normalization, synchronous updates, clipping, iteration indexing; deck slides 2–3 | Verified |
| Initial state 0 and aligned positions/fitness/archive through final state | All 180 raw NPZ traces have 101 × 30 agents; RLS web 50 iterations gives 51 frames and 51 values; tests and actual browser checks | Verified |
| Same best-so-far definition across methods | Canonical archive implementation; tests count evaluated points and independently recompute archived values; all raw traces audited | Verified |
| 2D, 30 agents, 100 iterations, 30 runs per method/function | config.json; all 180 per-run JSON/NPZ/CSV; docs/verification/deliverables.json | Verified |
| Common bounds and explicit seed schedule, configuration in every run | config.json and per-run JSON; verifier checks every seed, bound, parameter and matched initial population | Verified |
| Private RNG and repeatability | NumPy global state test; exact equality repeat runs for both functions/all methods; preselected example reruns | Verified |
| Actual evaluations and runtime, no drawing/export time | Instrumented objective calls in core; counted-objective test; 3030 calls in every raw record; perf_counter search-only timer | Verified |
| Appropriate equal evaluation budget comparison | Caching makes actual budgets equal at 3030; plots/*_evaluations PNG/SVG; slides 4 and 10; no second invented dataset | Verified |
| CSV/JSON seed, parameters, final fitness, position, runtime, calls, history per run | runs/*.json and runs/*.csv plus runs.csv/runs.json; NPZ adds population fitness/positions; verifier checks aggregate/per-run equality | Verified |
| All 30 runs, no fabricated outcomes or cherry-picked winner | summaries recomputed from all records; deterministic seed schedule; median/worst/runtime caveats in RESULTS.md, deck and Q&A | Verified |
| Mean best-so-far ± SD, median, final distribution, summary table, optimality gap for both functions | 14 base statistical plot pairs (PNG/SVG), four additional slide pairs; summary.json/CSV and table plots; means, medians, sample SD, best/worst/runtime | Verified |
| Distinguish mean across runs from population mean | Plot labels and methodology; optional population_mean plots, per-run population mean data | Verified |
| Correct log zero handling, untouched raw numbers, readable labels | Display floor 1e-16 applied at plotting only; raw NPZ/CSV/JSON compared exactly; titles/axes/legends/units and high-resolution PNG/SVG inspected | Verified |
| Contour animation both functions with per-frame current agents, true optimum, archive, iteration and fitness | Shared canonical example traces, seed 424242; 101 actual GIF frames and MP4 decoded frames; exports inspected | Verified |
| Predetermined illustrative seed separate from statistics | config written before experiment; examples/ contains seed 424242, run 0; none included in 180 measured runs | Verified |
| GIF and MP4, snapshots 0/25/50/75/100 | animations/manifest.json; ffprobe + full decode; snapshots/*.png and *.svg; verifier checks required frames and example reproducibility | Verified |
| Rosenbrock valley visible and transformations disclosed | log10(1+f) contour, thin valley line, full bounds + fixed zoom with visible-agent count; animation decoded frame and snapshots inspected | Verified |
| Web choose function/method, run, play, pause, seek and accurate values | Real Chromium, six Sphere/Rosenbrock method combinations, full 30/100 GOA examples, reset/step, Compare All, Thai/English switch; browser.json and screenshots | Verified |
| 10–12 slides covering theory, applications, setup, both functions, plots, comparisons, limitations, conclusions, references | Actual 12-page PPTX/PDF, rendered slide pages/contact sheet, script; deck titles/content match supplied outline | Verified |
| Approx. 12 minutes, no more than 15; separate Thai script | slide_plan.json sums to 720 seconds; 10,605-character Thai script includes media pauses and timed sections; rehearsal guidance explicitly distinguishes allocated time from measured speaking | Ready; presenter rehearsal remains a preparation step |
| At least eight Q&A answers including specified topics | presentation/qa_th.md contains 14 numbered questions/answers including all requested subjects | Verified |
| Performance claims follow real results | Exact table fitness and runtime strings checked in current PDF; all descriptive conclusions checked against summary.json; no significance/universal superiority claim | Verified |
| PPTX/PDF render without overflow, overlap or undersized plots | Actual LibreOffice conversion; PDF page bounds checked; all 12 pages visually inspected; enlarged paired-plot labels and moved media links after initial render review | Verified |
| Dependencies and README commands for install/tests/web/all exports/deck updates | requirements-workshop.txt and exact installed lock; README; full documented `python -m workshop all` executed successfully end-to-end | Verified |
| Old and new tests, API, actual browser checks, real exports | 29 tests + 10 subtests pass (pytest.txt); browser.json; deliverables.json; full rebuild console | Verified |
| Clear results/presentation/docs folders, no venv/cache/dependency commit | README deliverable index; .gitignore includes environments/caches/dependencies/runtime browser log; commit content is audited before publishing | Verified |
| Final report of changes, findings, tests, paths, commands and actual limitations | README + RESULTS.md + this audit + final response | Delivered |

## Visual review

All 12 PDF pages were reviewed using the actual rendered contact sheet, with detailed review of the comparison table and revised plot/illustration pages. Text and chart labels are inside their panels. The initial overlapping animation link and small chart labels were corrected before the final rebuild. PPTX and PDF hashes are recorded in export_status.json so an older PDF cannot silently masquerade as a successful new export. The PDF is a static fallback for motion; media is provided separately as playable GIF/MP4.

Browser evidence comes from Chromium running the actual Flask app on port 8091 because 8080 is occupied by another application. No existing service was stopped. The audit exercised UI events and compared Plotly marker positions, current agents and displayed fitness with the actual returned frame data. No external requests or page errors occurred. An animation-loading/seek race found during testing was fixed and the complete browser audit was rerun successfully.

## Scope and remaining limits

No required export is blocked: PPTX, PDF, PNG, SVG, GIF and MP4 were produced. Runtime is machine dependent; the equality of evaluation counts does not imply equal arithmetic work. GOA has the lowest observed median in both supplied tests, while RLS is faster and GOA has a worse Rosenbrock worst case. These findings do not prove statistical significance or general superiority. The coordinate/bound-normalized implementation is explicitly documented as a GOA variant. High-dimensional, multimodal, parameter-tuned and constrained applications were not requested as experiments and are identified as future work. The 12-minute timing is an allocated presentation plan; the actual presenter should rehearse to calibrate delivery speed.

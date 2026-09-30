# Methodology and implementation audit

## Source inspected

The supplied paper `ScienceDirect/1-s2.0-S0965997816305646-main.pdf` was inspected using its extracted text: printed p.33 Eq. (2.7), p.34 Eq. (2.8), and p.36/Fig.8 algorithm discussion. Bibliographic metadata was checked against the [publisher](https://www.sciencedirect.com/science/article/abs/pii/S0965997816305646) and [university record](https://research.usc.edu.au/esploro/outputs/journalArticle/Grasshopper-Optimisation-Algorithm-Theory-and-application/991136505002621?institution=61USC_INST). DOI: [10.1016/j.advengsoft.2017.01.004](https://doi.org/10.1016/j.advengsoft.2017.01.004).

## Canonical implementation

`algorithms/core.py` is the single implementation for GOA, GA and RLS. `algorithms/grasshopper.py`, `goa_v2.GOA_v2`, the web app, `animation_simple.run_goa_simple`, `snapshots_simple.run_goa`, both existing reports, and the new workshop pipeline all use it. Public positional parameters and tuple return shapes are retained; wrappers optionally expose an `OptimizationResult` through `return_details=True`. The GOA_v2 class retains its class interface and benchmark functions. `goa.py` and `goa_equations.py` remain historical educational examples, are not used for workshop results, and should not be mistaken for the canonical implementation.

GOA update for dimension d, using the old generation X and old best archive T:

```text
Delta_ijd = X_jd - X_id
D_ij = Euclidean norm(X_j - X_i)
u_ijd = Delta_ijd / D_ij       (zero for pairs with D_ij <= 1e-10)
r_ijd = clip(1 + 3*abs(Delta_ijd)/(ub_d-lb_d), 1, 4)
s(r) = f*exp(-r/l) - exp(-r)
c_t = c_max - t*(c_max-c_min)/T, t = 1..T
X_new_id = clip(T_d + c_t * sum_{j != i} [c_t*(ub_d-lb_d)/2*s(r_ijd)*u_ijd], lb_d, ub_d)
```

Both c factors and `(ub-lb)/2` in Eq.2.7 are preserved. Eq.2.8 gives the linear c schedule. T is best-so-far and is independent of the known optimum; gravity is omitted in the optimization form. All agents update synchronously from one old generation. Coincident-pair handling and clipping are explicitly defined.

The paper requires distance normalization into [1,4] and uses coordinate differences in Eq.2.7, but that alone does not specify a unique numerical normalization routine. **Our bound-scaled coordinate mapping is an implementation choice, not a claim of exact replication of the authors' software.** Direction still uses Euclidean distance. The original GOA_v2 already used a coordinate/bound mapping; we retained that choice, vectorized the same sums, and made it canonical. Its former “Paper-accurate” assertions were removed.

Earlier algorithms/grasshopper.py normalized Euclidean distance by the box diagonal. Earlier simple animation/snapshot copies clipped raw Euclidean distance to [1,4], omitted bound-width scaling and the inner c, and used c_min=1e-4. These were materially different dynamics. They now delegate to the canonical GOA. Former GOA schedules ran updates indexed 0..T-1 and did not reach c_min. The canonical update schedule is 1..T and reaches c_min at the last update, with initial random state stored at t=0. A scalar equation test covers the chosen normalization and both c factors.

## Baselines

GA retains real-number roulette selection (weights `max(fitness)-fitness+1e-10`), arithmetic crossover pc=0.8, per-individual Gaussian mutation pm=0.1 with sigma=0.1*(ub-lb), clipping, no population elitism, and an external best-so-far archive. Selection reuses cached deterministic fitness instead of reevaluating the population. It is the repository's educational GA baseline, not a tuned representative of all GA variants.

RLS runs N local searches independently. Proposals use Gaussian sigma=0.3 in coordinate units, clipping and acceptance if fitness <= cached current fitness. Current fitness is evaluated at initialization and replaced upon acceptance. The previous redundant old-point and population evaluations were removed. Its wrapper retains the prior step_size=0.1 default; the app and experiment explicitly use 0.3. Former RLS history omitted initialization: 50 updates produced 51 frames and 50 fitness values. All traces now include initialization and have T+1 aligned entries.

Every method's archive is the minimum objective among **all evaluated candidates through t**, including initial candidates. For RLS a rejected point cannot improve that archive, since its existing point is better. GOA/GA archive points need not still be present in the population. History, best position history, agent frames, population fitness and cumulative evaluation counts all use the same t=0..T index.

## Experiment configuration and fairness

Main experiment: 2D, 30 agents, 100 updates, 30 runs per algorithm/function; total 180 runs. Sphere bounds [-5,5]^2; Rosenbrock [-2,2]^2. Sphere f=sum x_i², known minimizer (0,0), f*=0; Rosenbrock f=100(x2-x1²)²+(x1-1)², minimizer (1,1), f*=0. Workshop bounds follow the prior web/demo bounds; the older objective-function report uses the supplied worksheet's Rosenbrock [-2.048,2.048] instead and is a separate experiment.

Function indices: Sphere=0, Rosenbrock=1. Run indices 0..29. Seed = 20260930 + 10000*function_index + run_index. Same seeds across algorithms pair their initial uniform populations; runs within each algorithm use distinct random streams. Each optimizer uses a private `default_rng`/PCG64 without affecting NumPy global state. Seeds/config are written before execution. Runtime order rotates across algorithms by run index, after short untimed warm-ups. There is no discarded statistical run or selection of favorable seeds.

Counting instruments actual scalar objective calls. With cached deterministic fitness, **all methods use N + N*T = 3030 calls**, including initial evaluations. Equal iteration and equal evaluation comparisons are therefore the same measured experiment, not an invented second dataset; plots also show actual cumulative evaluations. No contour, checking, chart, file export or video computation is charged as search evaluations. All objectives in this experiment are deterministic. Caching would require reconsideration for noisy objectives.

Runtime uses perf_counter and includes initialization, updates, objective evaluations and trace storage. It excludes serialization, charts and animation. Values are measurements on this machine, with environment and source hashes recorded in provenance.json; they are not hardware-independent speed claims. No parameter tuning, significance testing, or claims about general dominance were performed.

## Statistics and display

For each function/method all 30 raw runs feed summaries. Final fitness mean, median, sample SD (ddof=1), minimum, maximum and runtime mean/median/SD are exported. Convergence mean/median operate on **best-so-far across independent runs**. SD bands indicate variability, not confidence intervals. The optional population chart first averages current agents within each run and then averages those run means; labels distinguish it.

Optimality gap = best-so-far - known f*. Because both f*=0, gap and fitness coincide numerically here. These are objective errors, not coordinate distances. Raw JSON/CSV/NPZ retains true zero values. Log plots use a display floor epsilon=1e-16 only. Lower mean-SD bands may be negative, and are floored solely for log display; this is indicated on the plots. Boxplot whiskers use 1.5 IQR; all samples are shown, without random display jitter.

## Animation and presentation

Animation seed 424242 is fixed in config before experiments, shared by both function examples, and excluded from all 180-run statistics. Trace state t determines current red agents, known green optimum, orange best-so-far, displayed iteration and fitness. No final solution is shown as an earlier target. Example JSON/NPZ is saved separately. Frames 0,25,50,75,100 are exported. GIF and MP4 include all 101 frames at 6 fps (about 16.8 seconds). Rosenbrock contour color uses log10(1+f); titles and statistics show untransformed f. Full bounds plus a fixed zoom are shown, with the visible-agent count; agents outside zoom remain in the full view. Clustering is never treated as proof of optimality.

The deck has 12 slides, with a designed 720-second script excluding Q&A. Narration timing is a rehearsal allocation, not a measured presenter rehearsal. Slides carry exact measured tables and descriptive claims. MP4 hyperlinks are relative to the deliverable folder layout; PDF uses static snapshots. GIF/MP4 can be opened externally for playback. Only these smooth 2D tests have been performed; higher-dimensional, multimodal and constrained studies remain future work.

# Measured workshop results

All 180 runs are included; 30 per algorithm/function. Sample SD uses ddof=1. Lower fitness is better.

| Function | Method | Mean | Median | SD | Best | Worst | Mean time (s) | Evaluations |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| sphere | GOA | 3.425077e-08 | 3.543990e-08 | 2.367891e-08 | 8.285423e-11 | 9.557790e-08 | 0.016088 | 3030 |
| sphere | GA | 7.702990e-05 | 3.897103e-05 | 1.263872e-04 | 6.570364e-07 | 6.710191e-04 | 0.016509 | 3030 |
| sphere | RLS | 9.551993e-05 | 5.917428e-05 | 8.746641e-05 | 1.178213e-06 | 2.966109e-04 | 0.009398 | 3030 |
| rosenbrock | GOA | 2.035113e-03 | 1.957050e-04 | 8.238015e-03 | 2.659911e-07 | 4.526164e-02 | 0.023430 | 3030 |
| rosenbrock | GA | 1.050164e-01 | 5.996936e-02 | 1.150056e-01 | 1.580880e-04 | 4.403570e-01 | 0.023969 | 3030 |
| rosenbrock | RLS | 2.813466e-03 | 1.528462e-03 | 3.224871e-03 | 4.791074e-05 | 1.101043e-02 | 0.016091 | 3030 |

GOA has the lowest observed median in both functions for this configuration. RLS has the lowest mean measured runtime in both. GOA’s worst Rosenbrock run is worse than RLS’s worst run; GOA’s small median does not imply uniformly reliable performance. These are descriptive results, without significance testing or universal performance claims.

The optimality gap equals fitness here because both f* = 0. Equal evaluation counts arise from cached deterministic fitness: initial N plus N per update. Runtime is hardware dependent and excludes figures/export.

See config.json, provenance.json, runs/*.json, runs/*.csv, runs/*.npz and summary.csv.
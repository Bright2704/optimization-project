"""Full statistical experiment, independent of plotting/export."""
import csv
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from algorithms.core import optimize
from utils.objective_functions import paraboloid, rosenbrock

FUNCTIONS = {'sphere': (paraboloid, (-5., 5.), [0., 0.]),
             'rosenbrock': (rosenbrock, (-2., 2.), [1., 1.])}
ALGORITHMS = ('goa', 'ga', 'rls')
PARAMETERS = {'goa': dict(c_max=1., c_min=1e-5, f=0.5, l=1.5),
              'ga': dict(crossover_rate=0.8, mutation_rate=0.1),
              'rls': dict(step_size=0.3)}
ANIMATION_SEED = 424242  # preselected before inspecting any experimental outcomes
BASE_SEED = 20260930


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False), encoding='utf-8')


def configuration(runs=30, agents=30, iterations=100, base_seed=BASE_SEED):
    return dict(dimensions=2, runs_per_algorithm_function=runs, agents=agents,
                iterations=iterations, base_seed=base_seed, algorithms=ALGORITHMS,
                parameters=PARAMETERS, bounds={k:v[1] for k,v in FUNCTIONS.items()},
                known_optima={k:dict(position=v[2], fitness=0.) for k,v in FUNCTIONS.items()},
                seed_schedule='base_seed + 10000 * function_index + run_index (0-based); same seeds across algorithms',
                animation_seed=ANIMATION_SEED,
                comparison='equal iterations AND equal actual objective evaluations after caching; N*(T+1)',
                fitness_definition='minimum objective value among all evaluated points through iteration t',
                rng='numpy.random.default_rng / PCG64; no global RNG mutation',
                runtime_definition='perf_counter, initialization + search + trace storage; excludes plotting, files, animation',
                algorithm_order='rotate goa,ga,rls by run index; warm up each outside timed records',
                sd_definition='sample SD, ddof=1 (0 for a single run)',
                display_epsilon=1e-16)


def save_result(root, name, algorithm, run, seed, result, config, subdir='runs'):
    folder = root / subdir
    folder.mkdir(parents=True, exist_ok=True)
    stem = f'{name}_{algorithm}_{run:02d}'
    record = dict(function=name, algorithm=algorithm, run=run, seed=seed,
                  dimensions=2, agents=config['agents'], iterations=config['iterations'],
                  lower_bound=[FUNCTIONS[name][1][0]]*2, upper_bound=[FUNCTIONS[name][1][1]]*2,
                  parameters=PARAMETERS[algorithm], final_best_fitness=result.best_fitness,
                  best_position=result.best_position.tolist(), runtime_seconds=result.runtime_seconds,
                  evaluation_count=result.evaluation_count, convergence_history=result.history,
                  best_positions_history=[p.tolist() for p in result.best_positions_history],
                  evaluation_history=result.evaluations_history,
                  population_mean_history=[float(x.mean()) for x in result.population_fitness_history],
                  trace_file=f'{subdir}/{stem}.npz', history_csv=f'{subdir}/{stem}.csv')
    np.savez_compressed(folder / f'{stem}.npz', positions=np.array(result.positions_history),
                        population_fitness=np.array(result.population_fitness_history),
                        best_positions=np.array(result.best_positions_history),
                        best_fitness=np.array(result.history), evaluations=np.array(result.evaluations_history))
    with (folder / f'{stem}.csv').open('w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['iteration','best_so_far','best_x1','best_x2','population_mean_fitness','evaluations'])
        for t, fit in enumerate(result.history):
            writer.writerow([t,fit,*result.best_positions_history[t],record['population_mean_history'][t],result.evaluations_history[t]])
    save_json(folder / f'{stem}.json', record)
    return record


def summaries(records):
    rows = []
    for name in FUNCTIONS:
        for algorithm in ALGORITHMS:
            group = [r for r in records if r['function']==name and r['algorithm']==algorithm]
            if not group:
                raise ValueError(f'missing runs: {name}/{algorithm}')
            fitness = np.array([r['final_best_fitness'] for r in group])
            runtimes = np.array([r['runtime_seconds'] for r in group])
            counts = np.array([r['evaluation_count'] for r in group])
            rows.append(dict(function=name, algorithm=algorithm, n_runs=len(group),
                             mean=float(fitness.mean()), median=float(np.median(fitness)),
                             sd=float(fitness.std(ddof=1)) if len(group)>1 else 0.,
                             best=float(fitness.min()), worst=float(fitness.max()),
                             runtime_mean_s=float(runtimes.mean()), runtime_median_s=float(np.median(runtimes)),
                             runtime_sd_s=float(runtimes.std(ddof=1)) if len(group)>1 else 0.,
                             evaluations_min=int(counts.min()), evaluations_max=int(counts.max())))
    return rows


def source_hashes():
    paths = [Path('algorithms/core.py'), Path('workshop/experiments.py'), Path('utils/objective_functions.py')]
    return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def run_experiments(root=Path('results/workshop'), runs=30, agents=30, iterations=100, base_seed=BASE_SEED):
    root = Path(root); root.mkdir(parents=True, exist_ok=True)
    if runs<1 or agents<2 or iterations<1:
        raise ValueError('require runs>=1, agents>=2, iterations>=1')
    config = configuration(runs,agents,iterations,base_seed)
    # Write configuration before the first run, including the animation seed.
    save_json(root / 'config.json', config)
    for algorithm in ALGORITHMS:
        optimize(algorithm, paraboloid, 2, [-5]*2,[5]*2, agents,2,0,**PARAMETERS[algorithm])
    records=[]
    for fi,(name,(function,bounds,_)) in enumerate(FUNCTIONS.items()):
        for i in range(runs):
            seed=base_seed + 10000*fi+i
            order=ALGORITHMS[i%3:]+ALGORITHMS[:i%3]
            for algorithm in order:
                result=optimize(algorithm,function,2,[bounds[0]]*2,[bounds[1]]*2,
                                agents,iterations,seed,track_positions=True,**PARAMETERS[algorithm])
                record=save_result(root,name,algorithm,i+1,seed,result,config)
                record['execution_order_within_run']=order.index(algorithm)+1
                # Include order in both aggregate and per-run JSON.
                save_json(root/'runs'/f'{name}_{algorithm}_{i+1:02d}.json',record)
                records.append(record)
        print(f'{name}: {runs*3} measured runs completed',flush=True)
    save_json(root / 'runs.json', records)
    with (root/'runs.csv').open('w',newline='') as handle:
        fields=list(records[0])
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
        for r in records:
            writer.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()})
    summary=summaries(records); save_json(root/'summary.json',summary)
    with (root/'summary.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    metadata=dict(created_utc=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),
                  numpy=np.__version__,platform=platform.platform(),processor=platform.processor(),
                  source_sha256=source_hashes(),run_count=len(records),configuration='config.json')
    save_json(root/'provenance.json',metadata)
    return records


def animation_runs(root=Path('results/workshop')):
    root=Path(root)
    config=json.loads((root/'config.json').read_text())
    examples=[]
    for name,(function,bounds,_) in FUNCTIONS.items():
        result=optimize('goa',function,2,[bounds[0]]*2,[bounds[1]]*2,
                        config['agents'],config['iterations'],config['animation_seed'],**PARAMETERS['goa'])
        record=save_result(root,name,'goa',0,config['animation_seed'],result,config,'examples')
        record['purpose']='preselected single illustration; excluded from all statistical summaries'
        save_json(root/'examples'/f'{name}_goa_00.json',record)
        examples.append(record)
    return examples

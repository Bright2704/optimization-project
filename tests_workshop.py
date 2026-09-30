"""Scientific correctness and integration tests (including legacy interfaces)."""
import json
from pathlib import Path
import numpy as np
import pytest
from algorithms.core import optimize, goa_step
from workshop.experiments import FUNCTIONS, ALGORITHMS, PARAMETERS, summaries, configuration
from app import app
from goa_v2 import GOA_v2


@pytest.mark.parametrize('algorithm',ALGORITHMS)
@pytest.mark.parametrize('name',FUNCTIONS)
def test_trace_invariants_and_reproducibility(algorithm,name):
    func,bounds,optimum=FUNCTIONS[name]
    assert func(optimum)==0.
    args=(algorithm,func,2,[bounds[0]]*2,[bounds[1]]*2,8,12,13)
    before=np.random.get_state()
    result=optimize(*args,**PARAMETERS[algorithm]); repeat=optimize(*args,**PARAMETERS[algorithm])
    after=np.random.get_state()
    assert all(np.array_equal(a,b) for a,b in zip(before,after))
    assert len(result.history)==len(result.positions_history)==len(result.best_positions_history)==13
    assert len(result.population_fitness_history)==len(result.evaluations_history)==13
    assert np.all(np.diff(result.history)<=0)
    np.testing.assert_array_equal(result.positions_history,repeat.positions_history)
    np.testing.assert_array_equal(result.history,repeat.history)
    assert result.evaluation_count==8*13
    for t,(positions,fitness,best,fit) in enumerate(zip(result.positions_history,result.population_fitness_history,result.best_positions_history,result.history)):
        assert np.all(positions>=bounds[0]) and np.all(positions<=bounds[1])
        np.testing.assert_allclose(fitness,[func(p) for p in positions],rtol=1e-13)
        assert func(best)==pytest.approx(fit,rel=1e-13,abs=0)
        assert fit==pytest.approx(min(np.min(x) for x in result.population_fitness_history[:t+1]))
        assert result.evaluations_history[t]==8*(t+1)
    np.testing.assert_array_equal(result.best_position,result.best_positions_history[-1])
    assert result.best_fitness==result.history[-1]


def test_evaluation_count_is_actual_calls():
    for algorithm in ALGORITHMS:
        calls=[]
        def counted(x):calls.append(x.copy());return float(np.sum(x*x))
        r=optimize(algorithm,counted,2,[-2]*2,[2]*2,5,7,33)
        assert len(calls)==r.evaluation_count==40
        assert r.best_fitness==min(float(np.sum(p*p)) for p in calls)


def test_goa_equation_matches_scalar_reference():
    positions=np.array([[-2.,1.],[0.,0.],[1.,-1.],[1.,-1.]])
    lb=np.array([-3.,-2.]);ub=np.array([3.,4.]);target=positions[1];c=.3
    expected=[]
    for i in range(len(positions)):
        force=np.zeros(2)
        for j in range(len(positions)):
            diff=positions[j]-positions[i];distance=np.linalg.norm(diff)
            if distance<=1e-10:continue
            for d in range(2):
                r=1+3*abs(diff[d])/(ub[d]-lb[d])
                force[d]+=c*(ub[d]-lb[d])/2*(.5*np.exp(-r/1.5)-np.exp(-r))*diff[d]/distance
        expected.append(np.clip(c*force+target,lb,ub))
    np.testing.assert_allclose(goa_step(positions,target,lb,ub,c),expected,rtol=1e-14,atol=1e-14)


def test_legacy_goa_and_animation_share_canonical_trace():
    from animation_simple import run_goa_simple, sphere
    from snapshots_simple import run_goa
    from algorithms import grasshopper_optimization, genetic_algorithm, random_local_search
    args=dict(fitness_func=FUNCTIONS['sphere'][0],n_variables=2,lower_bound=[-5]*2,upper_bound=[5]*2,max_iter=6,seed=99,track_positions=True)
    canonical=optimize('goa',FUNCTIONS['sphere'][0],2,[-5]*2,[5]*2,7,6,99)
    legacy=grasshopper_optimization(**args,n_grasshoppers=7)
    np.testing.assert_array_equal(legacy[3],canonical.positions_history)
    goa=GOA_v2(FUNCTIONS['sphere'][0],2,[-5]*2,[5]*2,7,6,seed=99);goa.optimize(False)
    np.testing.assert_array_equal(goa.positions_history,canonical.positions_history)
    positions,bests=run_goa_simple(sphere,7,6,(-5,5),99)
    snapshots=run_goa(sphere,7,6,(-5,5),99)
    np.testing.assert_array_equal([np.column_stack(p) for p in positions],canonical.positions_history)
    np.testing.assert_array_equal(bests,canonical.best_positions_history)
    np.testing.assert_array_equal([np.column_stack(p[:2]) for p in snapshots],canonical.positions_history)
    for function,extra in [(random_local_search,{'n_agents':7}),(genetic_algorithm,{'pop_size':7})]:
        r=function(**args,**extra);assert len(r[2])==len(r[3])==7


def test_summaries_include_every_run_and_sample_sd():
    records=[]
    for name in FUNCTIONS:
        for a in ALGORITHMS:
            for f,t in [(1.,2.),(2.,4.),(30.,6.),(100.,8.)]:
                records.append(dict(function=name,algorithm=a,final_best_fitness=f,runtime_seconds=t,evaluation_count=3030))
    result=summaries(records)
    for row in result:
        assert row['n_runs']==4
        assert row['mean']==33.25
        assert row['median']==16.
        assert row['sd']==pytest.approx(np.std([1,2,30,100],ddof=1))
        assert row['best']==1 and row['worst']==100
        assert row['runtime_mean_s']==5.


@pytest.mark.parametrize('algorithm',ALGORITHMS)
@pytest.mark.parametrize('name',FUNCTIONS)
def test_api_frame_alignment_and_raw_precision(algorithm,name):
    client=app.test_client()
    payload=dict(algorithm=algorithm,function=name,n_agents=7,max_iter=50,seed=321)
    response=client.post('/api/run_animation',json=payload)
    assert response.status_code==200;data=response.get_json()
    assert len(data['history'])==data['n_frames']==len(data['frames'])==51
    assert data['known_optimum']['position']==FUNCTIONS[name][2]
    func=FUNCTIONS[name][0]
    for fit,best in zip(data['history'],data['best_positions_history']):
        assert func(best)==pytest.approx(fit,rel=1e-13,abs=0)
    repeat=client.post('/api/run',json=payload).get_json()
    assert repeat['history']==data['history'] and repeat['fitness']==data['fitness']
    assert data['evaluation_count']==357


def test_api_errors_and_offline_plotly():
    client=app.test_client()
    for payload in [[],None,{'algorithm':'invalid'},{'function':'invalid'},{'seed':-1},{'n_agents':1},{'max_iter':-1}]:
        assert client.post('/api/run',json=payload).status_code==400
    assert client.get('/assets/plotly.min.js').status_code==200
    contour=client.post('/api/contour',json={'function':'rosenbrock'}).get_json()
    np.testing.assert_allclose(contour['color_z'],np.log10(1+np.array(contour['z'])))


def test_invalid_optimizer_parameters():
    for kwargs in [dict(n_agents=1),dict(max_iter=-1),dict(mutation_rate=1.1),dict(step_size=0),dict(l=0),dict(c_min=0),dict(f=np.nan)]:
        with pytest.raises(ValueError):
            optimize('goa',FUNCTIONS['sphere'][0],2,[-5]*2,[5]*2,**kwargs)


def test_zero_iterations_is_a_valid_initial_state():
    for algorithm in ALGORITHMS:
        r=optimize(algorithm,FUNCTIONS['sphere'][0],2,[-5]*2,[5]*2,4,0,77)
        assert len(r.history)==len(r.positions_history)==1 and r.evaluation_count==4

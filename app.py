"""
=============================================================================
    Optimization Algorithms - Web Demo
    ===================================
    Flask web app สำหรับทดลอง algorithms แบบ visual

    วิธีใช้:
        python app.py
        เปิด browser ไปที่ http://localhost:5000
=============================================================================
"""

from flask import Flask, render_template, jsonify, request, send_file
import numpy as np
from pathlib import Path
from time import perf_counter
from algorithms.core import optimize

# Import algorithms
from utils.objective_functions import paraboloid as sphere, rosenbrock, rastrigin

app = Flask(__name__)


# =============================================================================
# Objective Functions
# =============================================================================

# Dictionary ของ functions
FUNCTIONS = {
    'sphere': {
        'func': sphere,
        'name': 'Sphere',
        'formula': 'f(x) = x₁² + x₂²',
        'minimum': '0 at (0, 0)',
        'bounds': (-5, 5), 'optimum_position': [0, 0], 'optimum_fitness': 0.0
    },
    'rastrigin': {
        'func': rastrigin,
        'name': 'Rastrigin',
        'formula': 'f(x) = 20 + x₁² + x₂² - 10(cos(2πx₁) + cos(2πx₂))',
        'minimum': '0 at (0, 0)',
        'bounds': (-5.12, 5.12), 'optimum_position': [0, 0], 'optimum_fitness': 0.0
    },
    'rosenbrock': {
        'func': rosenbrock,
        'name': 'Rosenbrock',
        'formula': 'f(x) = 100(x₂ - x₁²)² + (x₁ - 1)²',
        'minimum': '0 at (1, 1)',
        'bounds': (-2, 2), 'optimum_position': [1, 1], 'optimum_fitness': 0.0
    }
}


# =============================================================================
# Routes
# =============================================================================

@app.route('/')
def index():
    """หน้าแรก"""
    return render_template('index.html')


@app.route('/api/functions')
def get_functions():
    """ส่งรายชื่อ functions กลับ"""
    result = {}
    for key, val in FUNCTIONS.items():
        result[key] = {
            'name': val['name'],
            'formula': val['formula'],
            'minimum': val['minimum'],
            'bounds': val['bounds']
        }
    return jsonify(result)


@app.route('/assets/plotly.min.js')
def plotly_asset():
    """Bundled dependency for an offline workshop demo."""
    import plotly
    return send_file(Path(plotly.__file__).parent / "package_data" / "plotly.min.js",
                     mimetype="text/javascript")


def run_request(include_frames):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Expected a JSON object"), 400
    try:
        algorithm = data.get("algorithm", "goa")
        function_name = data.get("function", "sphere")
        if algorithm not in {"goa", "ga", "rls"} or function_name not in FUNCTIONS:
            raise ValueError("Unknown algorithm or function")
        n_agents = int(data.get("n_agents", 30))
        max_iter = int(data.get("max_iter", 100))
        seed = int(data.get("seed", 424242))
        if not 2 <= n_agents <= 100 or not 0 <= max_iter <= 1000 or seed < 0:
            raise ValueError("Require 2..100 agents, 0..1000 iterations, nonnegative seed")
        info = FUNCTIONS[function_name]
        bounds = info["bounds"]
        result = optimize(algorithm, info["func"], 2, [bounds[0]]*2, [bounds[1]]*2,
                          n_agents, max_iter, seed, track_positions=include_frames)
    except (ValueError, TypeError, OverflowError) as error:
        return jsonify(error=str(error)), 400
    payload = {
        "algorithm": {"goa": "Grasshopper (GOA)", "ga": "Genetic Algorithm",
                      "rls": "Random Local Search"}[algorithm],
        "function": info["name"], "position": result.best_position.tolist(),
        "fitness": result.best_fitness, "history": result.history, "bounds": bounds,
        "best_positions_history": [x.tolist() for x in result.best_positions_history],
        "population_mean_history": [float(np.mean(x)) for x in result.population_fitness_history],
        "evaluations_history": result.evaluations_history,
        "evaluation_count": result.evaluation_count, "runtime_seconds": result.runtime_seconds,
        "known_optimum": {"position": info["optimum_position"], "fitness": info["optimum_fitness"]},
        "seed": seed, "n_agents": n_agents,
    }
    if include_frames:
        payload.update(frames=[x.tolist() for x in result.positions_history],
                       n_frames=len(result.positions_history))
    return jsonify(payload)


@app.route('/api/run', methods=['POST'])
def run_algorithm():
    return run_request(False)


@app.route('/api/run_animation', methods=['POST'])
def run_animation():
    return run_request(True)


@app.route('/api/contour', methods=['POST'])
def get_contour():
    """สร้างข้อมูลสำหรับวาด contour plot"""
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify(error='Expected a JSON object'), 400
    function_name = data.get('function', 'sphere')

    if function_name not in FUNCTIONS:
        return jsonify(error='Unknown function'), 400
    func_info = FUNCTIONS[function_name]
    fitness_func = func_info['func']
    bounds = func_info['bounds']

    # สร้าง grid
    resolution = 100
    x = np.linspace(bounds[0], bounds[1], resolution)
    y = np.linspace(bounds[0], bounds[1], resolution)

    z = []
    for yi in y:
        row = []
        for xi in x:
            val = fitness_func([xi, yi])
            row.append(round(float(val), 4))
        z.append(row)

    return jsonify({
        'x': x.tolist(),
        'y': y.tolist(),
        'z': z,
        'color_z': np.log10(1 + np.array(z)).tolist() if function_name == 'rosenbrock' else z,
        'color_transform': 'log10(1 + f)' if function_name == 'rosenbrock' else 'f',
        'known_optimum': {'position': func_info['optimum_position'], 'fitness': 0.0},
        'bounds': bounds
    })


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    print("=" * 50)
    print("  Optimization Algorithms Web Demo")
    print(f"  Open: http://127.0.0.1:{args.port}")
    print("=" * 50)
    app.run(debug=False, port=args.port, host='127.0.0.1')

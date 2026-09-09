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

from flask import Flask, render_template, jsonify, request
import numpy as np
import json

# Import algorithms
from algorithms import random_local_search, genetic_algorithm, grasshopper_optimization

app = Flask(__name__)


# =============================================================================
# Objective Functions
# =============================================================================

def sphere(x):
    """Sphere: f(x) = sum(x_i^2), min = 0 at origin"""
    return float(np.sum(np.array(x)**2))

def rastrigin(x):
    """Rastrigin: highly multimodal, min = 0 at origin"""
    x = np.array(x)
    n = len(x)
    return float(10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x)))

def rosenbrock(x):
    """Rosenbrock: valley-shaped, min = 0 at (1,1)"""
    x = np.array(x)
    return float(np.sum(100 * (x[1:] - x[:-1]**2)**2 + (x[:-1] - 1)**2))

# Dictionary ของ functions
FUNCTIONS = {
    'sphere': {
        'func': sphere,
        'name': 'Sphere',
        'formula': 'f(x) = x₁² + x₂²',
        'minimum': '0 at (0, 0)',
        'bounds': (-5, 5)
    },
    'rastrigin': {
        'func': rastrigin,
        'name': 'Rastrigin',
        'formula': 'f(x) = 20 + x₁² + x₂² - 10(cos(2πx₁) + cos(2πx₂))',
        'minimum': '0 at (0, 0)',
        'bounds': (-5.12, 5.12)
    },
    'rosenbrock': {
        'func': rosenbrock,
        'name': 'Rosenbrock',
        'formula': 'f(x) = 100(x₂ - x₁²)² + (x₁ - 1)²',
        'minimum': '0 at (1, 1)',
        'bounds': (-2, 2)
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


@app.route('/api/run', methods=['POST'])
def run_algorithm():
    """รัน algorithm และส่งผลลัพธ์กลับ"""
    data = request.json

    # รับ parameters
    algorithm = data.get('algorithm', 'rls')
    function_name = data.get('function', 'sphere')
    n_agents = int(data.get('n_agents', 20))
    max_iter = int(data.get('max_iter', 50))

    # เลือก function
    func_info = FUNCTIONS.get(function_name, FUNCTIONS['sphere'])
    fitness_func = func_info['func']
    bounds = func_info['bounds']

    # Parameters
    n_variables = 2  # ใช้ 2D สำหรับ visualization
    lb = [bounds[0]] * n_variables
    ub = [bounds[1]] * n_variables

    # รัน algorithm
    if algorithm == 'rls':
        pos, fit, history = random_local_search(
            fitness_func=fitness_func,
            n_variables=n_variables,
            lower_bound=lb,
            upper_bound=ub,
            n_agents=n_agents,
            max_iter=max_iter,
            step_size=0.3
        )
        algo_name = 'Random Local Search'

    elif algorithm == 'ga':
        pos, fit, history = genetic_algorithm(
            fitness_func=fitness_func,
            n_variables=n_variables,
            lower_bound=lb,
            upper_bound=ub,
            pop_size=n_agents,
            max_iter=max_iter
        )
        algo_name = 'Genetic Algorithm'

    elif algorithm == 'goa':
        pos, fit, history = grasshopper_optimization(
            fitness_func=fitness_func,
            n_variables=n_variables,
            lower_bound=lb,
            upper_bound=ub,
            n_grasshoppers=n_agents,
            max_iter=max_iter
        )
        algo_name = 'Grasshopper (GOA)'

    else:
        return jsonify({'error': 'Unknown algorithm'}), 400

    # ส่งผลลัพธ์กลับ
    return jsonify({
        'algorithm': algo_name,
        'function': func_info['name'],
        'position': [round(float(p), 6) for p in pos],
        'fitness': round(float(fit), 8),
        'history': [round(float(h), 6) for h in history],
        'bounds': bounds
    })


@app.route('/api/contour', methods=['POST'])
def get_contour():
    """สร้างข้อมูลสำหรับวาด contour plot"""
    data = request.json
    function_name = data.get('function', 'sphere')

    func_info = FUNCTIONS.get(function_name, FUNCTIONS['sphere'])
    fitness_func = func_info['func']
    bounds = func_info['bounds']

    # สร้าง grid
    resolution = 50
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
        'bounds': bounds
    })


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    print("=" * 50)
    print("  Optimization Algorithms Web Demo")
    print("  Open: http://localhost:8080")
    print("=" * 50)
    app.run(debug=True, port=8080, host='127.0.0.1')

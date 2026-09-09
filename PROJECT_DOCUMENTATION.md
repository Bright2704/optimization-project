# Optimization Algorithms Project - Complete Documentation
## เอกสารอธิบายระบบทั้งหมด (สำหรับ AI และผู้ใช้)

---

## 1. ภาพรวม Project

### 1.1 วัตถุประสงค์
Project นี้สร้างขึ้นเพื่อ:
- ศึกษาและเปรียบเทียบ Optimization Algorithms
- สร้างระบบทดลองที่เข้าใจง่าย
- ใช้สำหรับ presentation และการเรียนรู้

### 1.2 Algorithms ที่มี
| # | Algorithm | ชื่อเต็ม | หลักการ |
|---|-----------|---------|---------|
| 1 | RLS | Random Local Search | สุ่มขยับตำแหน่ง ถ้าดีก็รับ |
| 2 | GA | Genetic Algorithm | Selection → Crossover → Mutation |
| 3 | GOA | Grasshopper Optimisation Algorithm | Social Force + Adaptive c |

### 1.3 Objective Functions
| Function | สูตร | Minimum | ลักษณะ |
|----------|------|---------|--------|
| Paraboloid | `Σ(x_i²)` | 0 at origin | ง่าย, unimodal |
| Rosenbrock | `Σ[100(x_{i+1}-x_i²)² + (x_i-1)²]` | 0 at (1,1,...) | Valley-shaped |
| Griewank | `1 + Σ(x_i²)/4000 - Π(cos(x_i/√i))` | 0 at origin | multimodal |
| Rastrigin | `10n + Σ(x_i² - 10cos(2πx_i))` | 0 at origin | highly multimodal |

---

## 2. โครงสร้างไฟล์

```
Optimization-project/
│
├── algorithms/                      # โฟลเดอร์เก็บ Algorithms
│   ├── __init__.py                 # Export functions
│   ├── random_local_search.py      # RLS algorithm
│   ├── genetic_algorithm.py        # GA algorithm
│   └── grasshopper.py              # GOA algorithm
│
├── utils/
│   └── objective_functions.py      # Objective functions 5 แบบ
│
├── templates/
│   └── index.html                  # หน้าเว็บหลัก
│
├── static/
│   ├── style.css                   # CSS styles
│   └── app.js                      # JavaScript
│
├── ScienceDirect/                  # เอกสารอ้างอิง
│   ├── GOA_Summary.md              # สรุป GOA paper
│   └── Algorithm_ws/               # PDF จาก workshop
│
├── app.py                          # Flask web server
├── run_demo.py                     # CLI demo
├── ALGORITHM_GUIDE.md              # คู่มือ algorithms
└── PROJECT_DOCUMENTATION.md        # เอกสารนี้
```

---

## 3. อธิบาย Algorithms แบบละเอียด

### 3.1 Random Local Search (RLS)

**ไฟล์:** `algorithms/random_local_search.py`

**หลักการ:**
```
1. สร้าง agents สุ่มใน search space
2. ทุก iteration:
   - สุ่ม delta จาก Normal distribution
   - new_pos = old_pos + delta
   - ถ้า f(new_pos) < f(old_pos) → รับ new_pos
3. Return ตำแหน่งที่ดีที่สุด
```

**Parameters:**
| Parameter | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------------|----------|
| n_agents | 30 | จำนวน agents |
| max_iter | 100 | จำนวน iterations |
| step_size | 0.1 | ขนาดการขยับ (std) |

**ข้อดี:** ง่ายมาก, implement ไว
**ข้อเสีย:** ติด local optima ง่าย

---

### 3.2 Genetic Algorithm (GA)

**ไฟล์:** `algorithms/genetic_algorithm.py`

**หลักการ:**
```
1. Initialize population สุ่ม
2. ทุก generation:
   a. Selection (Roulette Wheel):
      - คำนวณ probability จาก fitness
      - เลือก parents ตาม probability

   b. Crossover (Arithmetic):
      - alpha = random(0, 1)
      - child1 = alpha * parent1 + (1-alpha) * parent2
      - child2 = (1-alpha) * parent1 + alpha * parent2

   c. Mutation (Gaussian):
      - ถ้า random < mutation_rate:
        - individual += Normal(0, 0.1)

3. Return best individual
```

**Parameters:**
| Parameter | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------------|----------|
| pop_size | 30 | ขนาด population |
| max_iter | 100 | จำนวน generations |
| crossover_rate | 0.8 | อัตราการ crossover |
| mutation_rate | 0.1 | อัตราการ mutation |

**ข้อดี:** หลีกเลี่ยง local optima ได้ดี
**ข้อเสีย:** ต้อง tune parameters

---

### 3.3 Grasshopper Optimisation Algorithm (GOA)

**ไฟล์:** `algorithms/grasshopper.py`

**หลักการ (จาก Saremi et al., 2017):**

**1. Social Force Function:**
```
s(r) = f * exp(-r/l) - exp(-r)

โดย: f = 0.5 (intensity), l = 1.5 (length scale)

ผลลัพธ์:
- r < 2.079: s(r) < 0 → Repulsion (ผลักกัน)
- r = 2.079: s(r) = 0 → Comfort zone
- r > 2.079: s(r) > 0 → Attraction (ดึงดูด)
```

**2. Adaptive Coefficient c:**
```
c = c_max - iter * (c_max - c_min) / max_iter

โดย: c_max = 1, c_min = 0.00001

ผลลัพธ์:
- เริ่มต้น c สูง → exploration (สำรวจกว้าง)
- ตอนท้าย c ต่ำ → exploitation (ค้นหาละเอียด)
```

**3. Position Update:**
```
X_i = c * S_i + Target

โดย:
- S_i = Σ c * (ub-lb)/2 * s(r_ij) * direction_ij
- Target = ตำแหน่งที่ดีที่สุดที่หาได้
```

**Parameters:**
| Parameter | ค่าเริ่มต้น | คำอธิบาย |
|-----------|------------|----------|
| n_grasshoppers | 30 | จำนวนตั๊กแตน |
| max_iter | 100 | จำนวน iterations |
| c_max | 1.0 | ค่า c เริ่มต้น |
| c_min | 0.00001 | ค่า c สุดท้าย |
| f | 0.5 | intensity of attraction |
| l | 1.5 | attractive length scale |

**ข้อดี:** Balance exploration/exploitation อัตโนมัติ
**ข้อเสีย:** O(N²) complexity

---

## 4. วิธีใช้งาน

### 4.1 รัน Web Demo
```bash
cd Optimization-project
source venv/bin/activate  # (ถ้าใช้ virtual environment)
python app.py
```
เปิด browser: http://localhost:5000

### 4.2 รัน CLI Demo
```bash
python run_demo.py
```

### 4.3 ใช้ในโค้ด Python
```python
from algorithms import random_local_search, genetic_algorithm, grasshopper_optimization
from utils.objective_functions import rastrigin, BOUNDS

# ตัวอย่าง: รัน GA กับ Rastrigin
bounds = BOUNDS['rastrigin']
pos, fit, history = genetic_algorithm(
    fitness_func=rastrigin,
    n_variables=10,
    lower_bound=[bounds[0]] * 10,
    upper_bound=[bounds[1]] * 10,
    pop_size=30,
    max_iter=100
)

print(f"Best fitness: {fit}")
print(f"Best position: {pos}")
```

---

## 5. Web Application

### 5.1 โครงสร้าง

```
[Frontend]                    [Backend]
index.html  ←→  app.js  ←→  app.py  ←→  algorithms/
   ↓
style.css
```

### 5.2 API Endpoints

| Endpoint | Method | คำอธิบาย |
|----------|--------|----------|
| `/` | GET | หน้าเว็บหลัก |
| `/api/functions` | GET | รายชื่อ functions |
| `/api/run` | POST | รัน algorithm |
| `/api/contour` | POST | ข้อมูลสำหรับ contour plot |

### 5.3 Request/Response Format

**POST /api/run:**
```json
// Request
{
    "algorithm": "ga",
    "function": "rastrigin",
    "n_agents": 30,
    "max_iter": 100
}

// Response
{
    "algorithm": "Genetic Algorithm",
    "function": "Rastrigin",
    "position": [0.001234, -0.002345],
    "fitness": 0.00001234,
    "history": [100.5, 50.2, 25.1, ...],
    "bounds": [-5.12, 5.12]
}
```

---

## 6. ผลการทดสอบ

### 6.1 ผลลัพธ์ 5D (30 agents, 100 iterations)

| Function | RLS | GA | GOA | Winner |
|----------|-----|-----|-----|--------|
| Paraboloid | 0.024 | 0.086 | **0.00002** | GOA |
| Rosenbrock | 1.557 | 4.854 | **1.526** | GOA |
| Griewank | 18.395 | 0.563 | **0.179** | GOA |
| Rastrigin | 25.553 | **4.195** | 9.951 | GA |

### 6.2 สรุป
- **GOA** ดีที่สุดสำหรับ functions ส่วนใหญ่
- **GA** ดีกว่าสำหรับ highly multimodal (Rastrigin)
- **RLS** ง่ายแต่ผลลัพธ์ไม่ค่อยดี

---

## 7. Key Concepts

### 7.1 Exploration vs Exploitation
- **Exploration:** สำรวจพื้นที่กว้าง หาบริเวณที่มี potential
- **Exploitation:** ค้นหาละเอียดในบริเวณที่ดี

### 7.2 Local Optima Problem
- ปัญหา: Algorithm อาจติดอยู่ที่ local minimum
- วิธีแก้:
  - GA: Crossover + Mutation สร้างความหลากหลาย
  - GOA: Repulsion force ผลักออกจาก local optima

### 7.3 No Free Lunch Theorem
> ไม่มี algorithm ที่ดีที่สุดสำหรับทุกปัญหา

---

## 8. Dependencies

```
numpy       # การคำนวณ
flask       # web server (สำหรับ web demo)
```

ติดตั้ง:
```bash
pip install numpy flask
```

---

## 9. References

1. **GOA Paper:** Saremi, S., Mirjalili, S., & Lewis, A. (2017). Grasshopper Optimisation Algorithm: Theory and application. Advances in Engineering Software, 105, 30-47.

2. **GA:** จาก workshop PDF `ScienceDirect/Algorithm_ws/l9-11.pdf`

3. **Objective Functions:** จาก `ScienceDirect/workshop_objective_function.pdf`

---

## 10. Quick Start for AI

### ถ้า AI ต้องการเข้าใจ project นี้:

1. **อ่านไฟล์นี้ก่อน** (`PROJECT_DOCUMENTATION.md`)

2. **ดูโครงสร้าง algorithms:**
   - `algorithms/random_local_search.py` - ง่ายที่สุด
   - `algorithms/genetic_algorithm.py` - GA
   - `algorithms/grasshopper.py` - GOA

3. **ดู objective functions:**
   - `utils/objective_functions.py`

4. **ทดลองรัน:**
   ```bash
   python run_demo.py  # CLI
   python app.py       # Web
   ```

### Key Files:
| ไฟล์ | หน้าที่ |
|------|--------|
| `algorithms/*.py` | Algorithms ทั้งหมด |
| `utils/objective_functions.py` | Test functions |
| `app.py` | Web server |
| `run_demo.py` | CLI demo |
| `templates/index.html` | หน้าเว็บ |
| `static/app.js` | Frontend logic |

---

## 11. Flowchart

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │   Web    │  │   CLI    │  │  Python  │                  │
│  │  (HTML)  │  │  (demo)  │  │  (code)  │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
└───────┼─────────────┼─────────────┼─────────────────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Algorithm Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │   RLS    │  │    GA    │  │   GOA    │                  │
│  │  (สุ่ม)  │  │ (วิวัฒน์) │  │ (ตั๊กแตน) │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
└───────┼─────────────┼─────────────┼─────────────────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                 Objective Functions                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Sphere   │  │Rosenbrock│  │ Griewank │  │Rastrigin │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

**Last Updated:** 2024
**Version:** 1.0

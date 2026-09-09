# Optimization Algorithms - Simple Guide
## คู่มืออธิบาย Algorithms แบบเข้าใจง่าย

---

## 1. โครงสร้าง Project

```
Optimization-project/
├── algorithms/                    # โฟลเดอร์เก็บ algorithms
│   ├── random_local_search.py    # RLS - ง่ายที่สุด
│   ├── genetic_algorithm.py      # GA - วิวัฒนาการ
│   └── grasshopper.py            # GOA - ตั๊กแตน
├── utils/
│   └── objective_functions.py    # ฟังก์ชันทดสอบ 5 แบบ
└── run_demo.py                   # ไฟล์ทดลองหลัก
```

---

## 2. สรุป 3 Algorithms

### 2.1 Random Local Search (RLS)
**แนวคิด:** ง่ายที่สุด - สุ่มขยับตำแหน่ง ถ้าดีกว่าเดิมก็รับ

```
Loop:
  1. สุ่มขยับตำแหน่งเล็กน้อย (Gaussian noise)
  2. ถ้า fitness ใหม่ดีกว่า → รับตำแหน่งใหม่
  3. ถ้าไม่ดีกว่า → อยู่ที่เดิม
```

**ข้อดี:** เข้าใจง่าย, implement ง่าย
**ข้อเสีย:** ติด local optima ง่าย

---

### 2.2 Genetic Algorithm (GA)
**แนวคิด:** จำลองวิวัฒนาการ - Selection, Crossover, Mutation

```
Loop:
  1. Selection: เลือกตัวที่ fitness ดี (Roulette Wheel)
  2. Crossover: ผสม genes ระหว่าง parents
     child = α*parent1 + (1-α)*parent2
  3. Mutation: เปลี่ยนแปลง genes แบบสุ่ม
```

**ข้อดี:** หลีกเลี่ยง local optima ได้ดี
**ข้อเสีย:** ต้อง tune parameters หลายตัว

---

### 2.3 Grasshopper Optimisation Algorithm (GOA)
**แนวคิด:** จำลองพฤติกรรมตั๊กแตน - ผลัก/ดึงดูดกัน

```
Social Force: s(r) = f*exp(-r/l) - exp(-r)
  - ใกล้กัน → ผลักกัน (repulsion)
  - ห่างกัน → ดึงดูด (attraction)

Position Update:
  X_new = c * [Social Interactions] + Target

Adaptive c: ลดจาก 1 → 0.00001
  - เริ่มต้น: สำรวจกว้าง (exploration)
  - ตอนท้าย: ค้นหาละเอียด (exploitation)
```

**ข้อดี:** Balance exploration/exploitation อัตโนมัติ
**ข้อเสีย:** O(N²) ต่อ iteration

---

## 3. Objective Functions

| Function    | สูตร                                    | Minimum | Domain       |
|-------------|----------------------------------------|---------|--------------|
| Paraboloid  | `Σ(x_i²)`                              | 0       | [-5, 5]      |
| Rosenbrock  | `Σ[100(x_{i+1}-x_i²)² + (x_i-1)²]`    | 0       | [-2.048, 2.048] |
| Griewank    | `1 + Σ(x_i²)/4000 - Π(cos(x_i/√i))`  | 0       | [-600, 600]  |
| Schwefel    | `418.98n - Σ(x_i*sin(√|x_i|))`        | ≈0      | [-500, 500]  |
| Rastrigin   | `10n + Σ(x_i² - 10cos(2πx_i))`        | 0       | [-5.12, 5.12] |

---

## 4. วิธีใช้งาน

### รันทดสอบทั้งหมด:
```bash
python run_demo.py
```

### ใช้ algorithm เดี่ยว:
```python
from algorithms import random_local_search, genetic_algorithm, grasshopper_optimization
from utils.objective_functions import rastrigin, BOUNDS

# เลือก algorithm
pos, fit, history = genetic_algorithm(
    fitness_func=rastrigin,
    n_variables=10,
    lower_bound=[-5.12] * 10,
    upper_bound=[5.12] * 10,
    pop_size=30,
    max_iter=100
)

print(f"Best: {fit}")
```

---

## 5. ผลการทดสอบ (5D)

| Function    | RLS       | GA        | GOA       | Winner |
|-------------|-----------|-----------|-----------|--------|
| Paraboloid  | 0.024     | 0.086     | **0.00002** | GOA    |
| Rosenbrock  | 1.557     | 4.854     | **1.526** | GOA    |
| Griewank    | 18.395    | 0.563     | **0.179** | GOA    |
| Rastrigin   | 25.553    | **4.195** | 9.951     | GA     |

---

## 6. Code อธิบายแบบง่าย

### RLS (10 บรรทัด):
```python
def rls(f, x, iterations):
    for _ in range(iterations):
        x_new = x + random_noise()       # สุ่มขยับ
        if f(x_new) < f(x):              # ถ้าดีกว่า
            x = x_new                     # รับตำแหน่งใหม่
    return x
```

### GA (20 บรรทัด):
```python
def ga(f, pop, iterations):
    for _ in range(iterations):
        # Selection - เลือกตัวดี
        fitness = [f(x) for x in pop]
        parents = select_best(pop, fitness)

        # Crossover - ผสม
        children = crossover(parents)

        # Mutation - กลายพันธุ์
        pop = mutate(children)
    return best(pop)
```

### GOA (25 บรรทัด):
```python
def goa(f, agents, iterations):
    target = best(agents)               # หาตัวที่ดีที่สุด

    for iter in range(iterations):
        c = 1 - iter/iterations         # ลด c ตามเวลา

        for i in range(len(agents)):
            S = 0
            for j in range(len(agents)):
                if i != j:
                    r = distance(agents[i], agents[j])
                    s = social_force(r)  # ผลัก/ดึงดูด
                    S += c * s * direction(i, j)

            agents[i] = c * S + target   # อัปเดตตำแหน่ง

        target = update_best(agents, target)
    return target
```

---

## 7. Key Takeaways

1. **RLS** - ง่ายแต่ติด local optima
2. **GA** - ดีกับ multimodal functions (หลาย local minima)
3. **GOA** - Balance ได้ดี, เหมาะกับปัญหาหลากหลาย

**No Free Lunch:** ไม่มี algorithm ที่ดีที่สุดสำหรับทุกปัญหา

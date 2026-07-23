# Grasshopper Optimisation Algorithm (GOA)
## สรุป Paper: ทฤษฎีและการประยุกต์ใช้

**ผู้แต่ง:** Shahrzad Saremi, Seyedali Mirjalili, Andrew Lewis
**วารสาร:** Advances in Engineering Software 105 (2017) 30–47
**มหาวิทยาลัย:** Griffith University, Australia

---

## 1. บทนำ (Introduction)

### 1.1 Optimization คืออะไร?
**Optimization** คือกระบวนการค้นหาค่าที่ดีที่สุดของตัวแปรในปัญหาเพื่อ **minimize** หรือ **maximize** ฟังก์ชันวัตถุประสงค์ (objective function)

### 1.2 ประเภทของปัญหา Optimization
| ประเภท | คำอธิบาย |
|--------|----------|
| **Continuous vs Discrete** | ตัวแปรเป็นค่าต่อเนื่องหรือค่าไม่ต่อเนื่อง |
| **Constrained vs Unconstrained** | มีข้อจำกัดหรือไม่มีข้อจำกัด |
| **Single-objective vs Multi-objective** | มีเป้าหมายเดียวหรือหลายเป้าหมาย |

### 1.3 ทำไมต้อง Metaheuristic Algorithm?

**ปัญหาของ Mathematical Optimization:**
- ติดอยู่ใน Local Optima (หาได้แค่คำตอบท้องถิ่น ไม่ใช่คำตอบที่ดีที่สุดจริงๆ)
- ต้องการข้อมูล Gradient ซึ่งบางปัญหาคำนวณยากหรือไม่รู้

**ข้อดีของ Stochastic/Metaheuristic:**
- ใช้ Random operators หลีกเลี่ยง local optima
- ไม่ต้องคำนวณ gradient
- มองปัญหาเป็น "Black Box" - เหมาะกับปัญหาจริงที่ไม่รู้ search space

### 1.4 No Free Lunch (NFL) Theorem
> ไม่มี algorithm ใดที่ดีที่สุดสำหรับทุกปัญหา - นี่คือแรงจูงใจในการพัฒนา algorithm ใหม่ๆ

---

## 2. แรงบันดาลใจจากธรรมชาติ: ตั๊กแตน (Grasshopper)

### 2.1 วงจรชีวิตตั๊กแตน
```
ไข่ (Egg) → ตัวอ่อน (Nymph) → ตัวเต็มวัย (Adult)
```

### 2.2 พฤติกรรมการรวมฝูง (Swarming Behavior)

| ระยะ | พฤติกรรม | เปรียบเทียบกับ Optimization |
|------|----------|----------------------------|
| **ตัวอ่อน (Nymph)** | เคลื่อนที่ช้า ก้าวเล็ก | **Exploitation** (ค้นหาในพื้นที่จำกัด) |
| **ตัวเต็มวัย (Adult)** | เคลื่อนที่ไกล รวดเร็ว | **Exploration** (สำรวจพื้นที่กว้าง) |

### 2.3 ปฏิสัมพันธ์ทางสังคมของตั๊กแตน
- **Repulsion (แรงผลัก):** เมื่ออยู่ใกล้กันเกินไป → ผลักกันออก
- **Attraction (แรงดึงดูด):** เมื่ออยู่ห่างกันพอเหมาะ → ดึงดูดเข้าหากัน
- **Comfort Zone:** ระยะที่สบาย ไม่มีแรงผลักหรือดึงดูด

---

## 3. แบบจำลองทางคณิตศาสตร์ (Mathematical Model)

### 3.1 สมการตำแหน่งพื้นฐาน

```
Xᵢ = Sᵢ + Gᵢ + Aᵢ
```

| สัญลักษณ์ | ความหมาย |
|-----------|----------|
| **Xᵢ** | ตำแหน่งของตั๊กแตนตัวที่ i |
| **Sᵢ** | Social Interaction (ปฏิสัมพันธ์ทางสังคม) |
| **Gᵢ** | Gravity Force (แรงโน้มถ่วง) |
| **Aᵢ** | Wind Advection (แรงลม) |

### 3.2 Social Interaction Function

```
Sᵢ = Σⱼ₌₁ᴺ s(dᵢⱼ) × d̂ᵢⱼ   (j ≠ i)
```

โดยที่:
- `dᵢⱼ = |xⱼ - xᵢ|` คือระยะห่างระหว่างตั๊กแตน i และ j
- `d̂ᵢⱼ = (xⱼ - xᵢ)/dᵢⱼ` คือ unit vector จาก i ไป j

### 3.3 ฟังก์ชัน s (Social Force Function)

```
s(r) = f × e^(-r/l) - e^(-r)
```

| พารามิเตอร์ | ความหมาย | ค่าที่ใช้ |
|-------------|----------|-----------|
| **f** | ความเข้มของแรงดึงดูด (intensity of attraction) | 0.5 |
| **l** | ระยะแรงดึงดูด (attractive length scale) | 1.5 |

### 3.4 โซนต่างๆ ของฟังก์ชัน s

```
         Repulsion Zone    Comfort Zone    Attraction Zone
              ↓                 ↓                ↓
    |←——————————————→|←———→|←————————————————————→|
    0              2.079         4              ∞
                    ↑
            (ไม่มีแรงผลัก/ดึงดูด)
```

- **ระยะ 0-2.079:** Repulsion (ผลักกัน)
- **ระยะ 2.079:** Comfort Zone (สบาย)
- **ระยะ > 2.079:** Attraction (ดึงดูด)

---

## 4. สมการหลักของ GOA สำหรับ Optimization

### 4.1 สมการอัปเดตตำแหน่ง

```
Xᵢᵈ = c × [ Σⱼ₌₁ᴺ c × (ubᵈ - lbᵈ)/2 × s(|xⱼᵈ - xᵢᵈ|) × (xⱼ - xᵢ)/dᵢⱼ ] + T̂ᵈ
```

| สัญลักษณ์ | ความหมาย |
|-----------|----------|
| **ubᵈ** | ขอบเขตบนของมิติที่ d |
| **lbᵈ** | ขอบเขตล่างของมิติที่ d |
| **T̂ᵈ** | Target (ค่าที่ดีที่สุดที่หาได้จนถึงตอนนี้) |
| **c** | ค่าสัมประสิทธิ์ที่ลดลงตามจำนวน iteration |

### 4.2 การคำนวณค่า c (Adaptive Coefficient)

```
c = cₘₐₓ - l × (cₘₐₓ - cₘᵢₙ) / L
```

| พารามิเตอร์ | ค่า |
|-------------|-----|
| **cₘₐₓ** | 1 |
| **cₘᵢₙ** | 0.00001 |
| **l** | iteration ปัจจุบัน |
| **L** | จำนวน iteration สูงสุด |

### 4.3 บทบาทของ c สองตัว

| ตำแหน่ง c | หน้าที่ |
|-----------|---------|
| **c ตัวนอก** | คล้าย inertial weight ใน PSO - ลดการเคลื่อนที่รอบ target |
| **c ตัวใน** | ลดขนาด attraction/repulsion zone ตาม iteration |

---

## 5. Pseudocode ของ GOA Algorithm

```
Initialize the swarm Xᵢ (i = 1, 2, ..., n)
Initialize cmax, cmin, and maximum number of iterations
Calculate the fitness of each search agent
T = the best search agent

while (l < Max number of iterations)
    Update c using Eq. (2.8)

    for each search agent
        Normalize the distances between grasshoppers in [1,4]
        Update the position of current search agent by Eq. (2.7)
        Bring the current search agent back if it goes outside boundaries
    end for

    Update T if there is a better solution
    l = l + 1
end while

Return T
```

---

## 6. ความแตกต่างระหว่าง GOA และ PSO

| ลักษณะ | PSO | GOA |
|--------|-----|-----|
| **Vector ต่อ particle** | 2 (position + velocity) | 1 (position เท่านั้น) |
| **การอัปเดตตำแหน่ง** | อิงจาก personal best + global best | อิงจาก global best + ตำแหน่งของ **ทุก** search agent |
| **การมีส่วนร่วม** | particle อื่นไม่มีส่วนร่วมโดยตรง | ทุก search agent มีส่วนร่วมในการอัปเดต |

---

## 7. กลไก Exploration vs Exploitation

### 7.1 การสมดุล

```
เริ่มต้น (Iteration น้อย)              ←→              สิ้นสุด (Iteration มาก)
        ↓                                                      ↓
   EXPLORATION                                           EXPLOITATION
   - c มีค่าสูง                                         - c มีค่าต่ำ
   - repulsion zone ใหญ่                                - repulsion zone เล็ก
   - เคลื่อนที่มาก                                      - เคลื่อนที่น้อย
   - สำรวจพื้นที่กว้าง                                  - ค้นหาในพื้นที่จำกัด
```

### 7.2 สรุปกลไก

| กลไก | ทำให้เกิด | ผลลัพธ์ |
|------|-----------|---------|
| **Repulsion** | Exploration | หลีกเลี่ยง local optima |
| **Attraction** | Exploitation | เข้าใกล้ global optimum |
| **Adaptive c** | Balance | สมดุลระหว่าง exploration และ exploitation |
| **Target (T)** | Convergence | รวมศูนย์ไปที่คำตอบที่ดีที่สุด |

---

## 8. การทดสอบ (Benchmarking)

### 8.1 ประเภท Test Functions

| ประเภท | ลักษณะ | ทดสอบอะไร |
|--------|--------|-----------|
| **Unimodal (F1-F7)** | มี global optimum เดียว | Exploitation & Convergence speed |
| **Multimodal (F8-F13)** | มี local optima มาก | Exploration & Local optima avoidance |
| **Composite (F14-F19)** | ผสมหลายลักษณะ | Overall balance |
| **CEC2005 (F1-F25)** | ท้าทายที่สุด | Real-world simulation |

### 8.2 Algorithm ที่เปรียบเทียบ

- PSO (Particle Swarm Optimization)
- GA (Genetic Algorithm)
- DE (Differential Evolution)
- GSA (Gravitational Search Algorithm)
- BA (Bat Algorithm)
- FPA (Flower Pollination Algorithm)
- FA (Firefly Algorithm)
- SMS (State of Matter Search)
- CS (Cuckoo Search)

### 8.3 ผลการทดสอบ

**GOA ให้ผลลัพธ์ที่ดีกว่าหรือเทียบเท่ากับ algorithm อื่นในส่วนใหญ่ของ test functions**

| Test Functions | ผลลัพธ์ GOA |
|----------------|-------------|
| Unimodal | ดีที่สุดในมากกว่าครึ่ง |
| Multimodal | ดีกว่าอย่างมีนัยสำคัญ |
| Composite | แข่งขันได้ดี |
| CEC2005 | ดีกว่าในส่วนใหญ่ |

---

## 9. การประยุกต์ใช้จริง (Real Applications)

### 9.1 Three-Bar Truss Design Problem

**เป้าหมาย:** Minimize น้ำหนักของโครงสร้าง truss 3 แท่ง

```
Variables: x = [x₁, x₂] = [A₁, A₂] (พื้นที่หน้าตัด)

Minimize: f(x) = (2√2·x₁ + x₂) × l

Subject to:
- g₁(x) = (√2·x₁ + x₂)/(√2·x₁² + 2x₁x₂) × P - σ ≤ 0
- g₂(x) = x₂/(√2·x₁² + 2x₁x₂) × P - σ ≤ 0
- g₃(x) = 1/(√2·x₂ + x₁) × P - σ ≤ 0

Variable range: 0 ≤ x₁, x₂ ≤ 1
Parameters: l = 100 cm, P = 2 KN/cm², σ = 2 KN/cm²
```

**ผลลัพธ์:**
| Algorithm | x₁ | x₂ | Optimal Weight | Max Eval |
|-----------|----|----|----------------|----------|
| **GOA** | 0.7889 | 0.4076 | **263.8959** | **13,000** |
| ALO | 0.7887 | 0.4083 | 263.8958 | 14,000 |
| PSO-DE | 0.7887 | 0.4082 | 263.8958 | 17,600 |

### 9.2 Cantilever Beam Design Problem

**เป้าหมาย:** Minimize น้ำหนักของคานยื่น 5 ส่วน

```
Variables: x = [x₁, x₂, x₃, x₄, x₅]

Minimize: f(x) = 0.6224(x₁ + x₂ + x₃ + x₄ + x₅)

Subject to: g(x) = 61/x₁³ + 27/x₂³ + 19/x₃³ + 7/x₄³ + 1/x₅³ - 1 ≤ 0

Variable range: 0.01 ≤ xᵢ ≤ 100
```

**ผลลัพธ์:**
| Algorithm | Optimal Weight | Max Eval |
|-----------|----------------|----------|
| **GOA** | 1.33996 | **13,000** |
| ALO | 1.33995 | 14,000 |
| CS | 1.33999 | 2,500 |

### 9.3 52-Bar Truss Design Problem

**เป้าหมาย:** Minimize น้ำหนักของโครงสร้าง truss 52 แท่ง (12 กลุ่ม)

**ผลลัพธ์:**
| Algorithm | Optimal Weight (kg) | No. of Analyses |
|-----------|---------------------|-----------------|
| **GOA** | **1902.605** | **2,300** |
| SOS | 1902.605 | 2,350 |
| PSO | 2230.16 | 150,000 |

---

## 10. วิธีการใช้งาน GOA

### 10.1 พารามิเตอร์ที่ต้องกำหนด

```python
# พารามิเตอร์หลัก
N = 30           # จำนวน search agents (grasshoppers)
Max_iter = 500   # จำนวน iterations สูงสุด
dim = 30         # จำนวนมิติของปัญหา
lb = -100        # ขอบเขตล่าง
ub = 100         # ขอบเขตบน

# พารามิเตอร์ของ GOA
cMax = 1         # ค่า c สูงสุด
cMin = 0.00001   # ค่า c ต่ำสุด
f = 0.5          # intensity of attraction
l = 1.5          # attractive length scale
```

### 10.2 ขั้นตอนการใช้งาน

```
1. กำหนดปัญหา
   - กำหนด objective function
   - กำหนด constraints (ถ้ามี)
   - กำหนด search space (lb, ub)

2. กำหนดพารามิเตอร์
   - จำนวน grasshoppers (N)
   - จำนวน iterations สูงสุด
   - cMax, cMin, f, l

3. Initialize
   - สร้าง random solutions N ตัว
   - คำนวณ fitness ของแต่ละตัว
   - หา target (ตัวที่ดีที่สุด)

4. Main Loop
   - อัปเดตค่า c ตาม iteration
   - normalize ระยะห่างใน [1,4]
   - อัปเดตตำแหน่งทุกตัวด้วย Eq. (2.7)
   - ตรวจสอบขอบเขต
   - อัปเดต target ถ้าเจอตัวที่ดีกว่า

5. Return
   - คืนค่า target (คำตอบที่ดีที่สุด)
```

### 10.3 การจัดการ Constraints

สำหรับปัญหาที่มี constraints ใช้ **Death Penalty:**
```python
if constraint_violated:
    fitness = very_large_number  # ลงโทษด้วยค่าสูงมาก
else:
    fitness = objective_function(x)
```

### 10.4 ตัวอย่าง Pseudocode (Python-like)

```python
import numpy as np

def s_func(r, f=0.5, l=1.5):
    """Social force function"""
    return f * np.exp(-r/l) - np.exp(-r)

def GOA(obj_func, lb, ub, dim, N=30, Max_iter=500):
    # Initialize
    cMax = 1
    cMin = 0.00001

    # Random initial population
    X = np.random.uniform(lb, ub, (N, dim))

    # Calculate initial fitness
    fitness = np.array([obj_func(x) for x in X])

    # Find best (target)
    best_idx = np.argmin(fitness)
    Target = X[best_idx].copy()
    Target_fitness = fitness[best_idx]

    # Main loop
    for iter in range(Max_iter):
        # Update c
        c = cMax - iter * (cMax - cMin) / Max_iter

        # Update each grasshopper
        for i in range(N):
            S = np.zeros(dim)

            for j in range(N):
                if i != j:
                    # Distance
                    dist = np.linalg.norm(X[j] - X[i])

                    # Normalize distance to [1,4]
                    dist_norm = 1 + 3 * (dist - np.min(dist)) / (np.max(dist) - np.min(dist) + 1e-10)

                    # Social force
                    s = s_func(dist_norm)

                    # Direction
                    direction = (X[j] - X[i]) / (dist + 1e-10)

                    # Accumulate
                    S += c * ((ub - lb) / 2) * s * direction

            # Update position
            X[i] = c * S + Target

            # Boundary check
            X[i] = np.clip(X[i], lb, ub)

        # Update fitness and target
        fitness = np.array([obj_func(x) for x in X])
        best_idx = np.argmin(fitness)

        if fitness[best_idx] < Target_fitness:
            Target = X[best_idx].copy()
            Target_fitness = fitness[best_idx]

    return Target, Target_fitness
```

---

## 11. ข้อดีและข้อจำกัดของ GOA

### 11.1 ข้อดี

| ข้อดี | คำอธิบาย |
|-------|----------|
| **Gradient-free** | ไม่ต้องคำนวณ gradient |
| **Black-box** | ใช้ได้กับปัญหาที่ไม่รู้ search space |
| **High exploration** | หลีกเลี่ยง local optima ได้ดี |
| **Adaptive** | ปรับสมดุล exploration/exploitation อัตโนมัติ |
| **Simple** | implement ง่าย |
| **Efficient** | ใช้ function evaluation น้อย |

### 11.2 ข้อจำกัด

| ข้อจำกัด | คำอธิบาย |
|----------|----------|
| **Single-objective only** | ใช้ได้กับปัญหาเป้าหมายเดียว |
| **Continuous variables** | ไม่รองรับตัวแปร discrete โดยตรง |
| **Computational cost** | O(N²) ต่อ iteration (ต้องคำนวณระยะห่างทุกคู่) |

---

## 12. ทิศทางการวิจัยในอนาคต (Future Work)

1. **Binary GOA** - สำหรับปัญหา discrete
2. **Multi-objective GOA** - สำหรับปัญหาหลายเป้าหมาย
3. **Hybrid GOA** - ผสมกับ algorithm อื่น
4. **Parameter tuning** - ศึกษาผลของพารามิเตอร์ต่างๆ
5. **Different comfort zone functions** - ทดลองฟังก์ชันรูปแบบอื่น

---

## 13. แหล่งข้อมูลเพิ่มเติม

**Source Code:**
- http://www.alimirjalili.com/Projects.html
- http://au.mathworks.com/matlabcentral/profile/authors/2943818-seyedali-mirjalili

---

## 14. สรุปสั้น (Quick Summary)

> **GOA** เป็น metaheuristic algorithm ที่จำลองพฤติกรรมการรวมฝูงของตั๊กแตน โดยใช้กลไก **repulsion** (ผลัก) และ **attraction** (ดึงดูด) ระหว่างตั๊กแตนเพื่อสำรวจและค้นหา optimal solution พร้อมด้วย **adaptive coefficient c** ที่ช่วยสมดุลระหว่าง exploration กับ exploitation อัตโนมัติตามจำนวน iteration

### Key Equations:
```
Position Update:  Xᵢᵈ = c × [Σ c × (ub-lb)/2 × s(|xⱼ-xᵢ|) × direction] + Target

Social Force:     s(r) = f × e^(-r/l) - e^(-r)

Adaptive c:       c = cₘₐₓ - iter × (cₘₐₓ - cₘᵢₙ) / Max_iter
```

### Key Parameters:
```
cMax = 1, cMin = 0.00001, f = 0.5, l = 1.5
```

---

*สร้างจาก Paper: "Grasshopper Optimisation Algorithm: Theory and application" - Saremi et al. (2017)*

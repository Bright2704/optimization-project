"""
Grasshopper Optimisation Algorithm (GOA)
=========================================
แบ่งตามสูตรใน Paper: Saremi et al. (2017)

สูตรทั้งหมดจาก Paper:
- Eq. 2.1: ตำแหน่งพื้นฐาน X_i = S_i + G_i + A_i
- Eq. 2.2: Social Interaction S_i
- Eq. 2.3: Social Force Function s(r)
- Eq. 2.4: Gravity Force G_i (ไม่ใช้ใน optimization)
- Eq. 2.5: Wind Advection A_i (กลายเป็น Target)
- Eq. 2.7: Position Update (สมการหลักสำหรับ optimization)
- Eq. 2.8: Adaptive Coefficient c
"""

import numpy as np
from typing import Callable, Tuple


# ============================================================================
# Eq. 2.3: Social Force Function
# ============================================================================
# s(r) = f × e^(-r/l) - e^(-r)
#
# Parameters:
#   f = 0.5 (intensity of attraction)
#   l = 1.5 (attractive length scale)
#
# Returns:
#   < 0 : Repulsion (ผลัก) เมื่อ r < 2.079
#   = 0 : Comfort Zone เมื่อ r = 2.079
#   > 0 : Attraction (ดึงดูด) เมื่อ r > 2.079
# ============================================================================

def eq_2_3_social_force(r: float, f: float = 0.5, l: float = 1.5) -> float:
    """
    Eq. 2.3: Social Force Function

    s(r) = f × e^(-r/l) - e^(-r)

    กำหนดแรงระหว่างตั๊กแตน:
    - r < 2.079: ผลักออก (repulsion)
    - r = 2.079: comfort zone
    - r > 2.079: ดึงดูด (attraction)
    """
    return f * np.exp(-r / l) - np.exp(-r)


# ============================================================================
# Eq. 2.8: Adaptive Coefficient c
# ============================================================================
# c = c_max - iteration × (c_max - c_min) / max_iterations
#
# Parameters:
#   c_max = 1 (ค่าเริ่มต้น - exploration สูง)
#   c_min = 0.00001 (ค่าสุดท้าย - exploitation สูง)
#
# หน้าที่:
#   - ลดลงเรื่อยๆ ตาม iteration
#   - ควบคุมสมดุล exploration/exploitation
# ============================================================================

def eq_2_8_adaptive_coefficient(
    iteration: int,
    max_iterations: int,
    c_max: float = 1.0,
    c_min: float = 0.00001
) -> float:
    """
    Eq. 2.8: Adaptive Coefficient c

    c = c_max - iteration × (c_max - c_min) / max_iterations

    ค่า c ลดลงจาก c_max → c_min ตาม iteration:
    - iteration 0: c = 1.0 (exploration สูง)
    - iteration สุดท้าย: c ≈ 0 (exploitation สูง)
    """
    return c_max - iteration * (c_max - c_min) / max_iterations


# ============================================================================
# Eq. 2.2: Social Interaction (ส่วนหนึ่งของ Eq. 2.7)
# ============================================================================
# S_i = Σ s(d_ij) × d̂_ij
#
# โดย:
#   d_ij = |x_j - x_i| (ระยะห่างระหว่างตั๊กแตน)
#   d̂_ij = (x_j - x_i) / d_ij (unit vector ทิศทาง)
# ============================================================================

def eq_2_2_social_interaction(
    grasshopper_i: np.ndarray,
    all_grasshoppers: np.ndarray,
    i: int
) -> np.ndarray:
    """
    Eq. 2.2: Social Interaction

    S_i = Σ s(d_ij) × d̂_ij  (สำหรับ j ≠ i)

    คำนวณผลรวมของแรงจากตั๊กแตนตัวอื่นทั้งหมด
    """
    n_grasshoppers = len(all_grasshoppers)
    n_variables = len(grasshopper_i)
    S = np.zeros(n_variables)

    for j in range(n_grasshoppers):
        if i != j:
            # d_ij = ระยะห่าง
            diff = all_grasshoppers[j] - grasshopper_i
            d_ij = np.linalg.norm(diff)

            if d_ij > 1e-10:
                # s(d_ij) = social force
                s_value = eq_2_3_social_force(d_ij)

                # d̂_ij = unit vector (ทิศทาง)
                d_hat = diff / d_ij

                # สะสมแรง
                S += s_value * d_hat

    return S


# ============================================================================
# Eq. 2.7: Position Update (สมการหลักสำหรับ Optimization)
# ============================================================================
# X_i^d = c × (Σ c × (ub_d - lb_d)/2 × s(|x_j^d - x_i^d|) × (x_j - x_i)/d_ij) + T̂_d
#
# ส่วนประกอบ:
#   c ตัวนอก: ลดการเคลื่อนที่รอบ target (คล้าย inertia weight ใน PSO)
#   c ตัวใน: ลดขนาด attraction/repulsion zone
#   (ub - lb)/2: ปรับขนาดตาม search space
#   s(...): social force (ผลัก/ดึงดูด)
#   (x_j - x_i)/d_ij: ทิศทาง
#   T̂_d: Target (คำตอบที่ดีที่สุด)
# ============================================================================

def eq_2_7_position_update(
    grasshopper_i: np.ndarray,
    all_grasshoppers: np.ndarray,
    i: int,
    target: np.ndarray,
    c: float,
    lower_bound: np.ndarray,
    upper_bound: np.ndarray
) -> np.ndarray:
    """
    Eq. 2.7: Position Update (Main Optimization Equation)

    X_i^d = c × (Σ c × (ub_d - lb_d)/2 × s(|x_j^d - x_i^d|) × (x_j - x_i)/d_ij) + T̂_d

    คำนวณตำแหน่งใหม่ของตั๊กแตนตัวที่ i
    """
    n_grasshoppers = len(all_grasshoppers)
    n_variables = len(grasshopper_i)

    # ผลรวมของ social interaction (ส่วน Σ)
    sum_social = np.zeros(n_variables)

    for j in range(n_grasshoppers):
        if i != j:
            # ระยะห่าง d_ij
            diff = all_grasshoppers[j] - grasshopper_i
            d_ij = np.linalg.norm(diff)

            if d_ij < 1e-10:
                continue

            # Normalize distance to [1, 4] (ตาม paper)
            # "normalize the distances between grasshoppers in [1,4]"
            d_normalized = 1 + (d_ij / np.max(upper_bound - lower_bound)) * 3
            d_normalized = np.clip(d_normalized, 1, 4)

            # s(d) = social force (Eq. 2.3)
            s_value = eq_2_3_social_force(d_normalized)

            # (x_j - x_i) / d_ij = unit vector (ทิศทาง)
            direction = diff / d_ij

            # c × (ub - lb)/2 × s × direction
            sum_social += c * ((upper_bound - lower_bound) / 2) * s_value * direction

    # X_i = c × (Σ ...) + Target
    new_position = c * sum_social + target

    # Boundary check
    new_position = np.clip(new_position, lower_bound, upper_bound)

    return new_position


# ============================================================================
# Eq. 2.1: Basic Position Model (สำหรับ reference - ไม่ใช้โดยตรง)
# ============================================================================
# X_i = S_i + G_i + A_i
#
# โดย:
#   S_i = Social Interaction (Eq. 2.2)
#   G_i = Gravity Force (Eq. 2.4) - ไม่ใช้ใน optimization
#   A_i = Wind Advection (Eq. 2.5) - กลายเป็น Target ใน Eq. 2.7
# ============================================================================

def eq_2_1_basic_position(S_i: np.ndarray, G_i: np.ndarray, A_i: np.ndarray) -> np.ndarray:
    """
    Eq. 2.1: Basic Position Model (Reference only)

    X_i = S_i + G_i + A_i

    หมายเหตุ: ใน GOA optimization:
    - G_i ถูกละเว้น (ไม่มีแรงโน้มถ่วง)
    - A_i กลายเป็น Target (ทิศทางลม = ทิศทางไปหาอาหาร)
    """
    return S_i + G_i + A_i


# ============================================================================
# GOA Algorithm (รวมทุกสมการ)
# ============================================================================

def GOA_algorithm(
    fitness_func: Callable,
    n_variables: int,
    lower_bound: np.ndarray,
    upper_bound: np.ndarray,
    n_grasshoppers: int = 30,
    max_iter: int = 500,
    verbose: bool = True
) -> Tuple[np.ndarray, float, list]:
    """
    Grasshopper Optimisation Algorithm

    Pseudocode จาก Paper (Fig. 8):
    1. Initialize the swarm X_i (i = 1, 2, ..., n)
    2. Initialize c_max, c_min, and maximum number of iterations
    3. Calculate the fitness of each search agent
    4. T = the best search agent
    5. while (l < Max number of iterations)
           Update c using Eq. (2.8)
           for each search agent
               Normalize the distances between grasshoppers in [1,4]
               Update the position of current search agent by Eq. (2.7)
               Bring the current search agent back if it goes outside boundaries
           end for
           Update T if there is a better solution
           l = l + 1
       end while
    6. Return T
    """
    lower_bound = np.array(lower_bound)
    upper_bound = np.array(upper_bound)

    # ====== Step 1: Initialize the swarm ======
    grasshoppers = np.random.uniform(
        low=lower_bound,
        high=upper_bound,
        size=(n_grasshoppers, n_variables)
    )

    if verbose:
        print("="*60)
        print("GOA Algorithm (ตามสูตรใน Paper)")
        print("="*60)
        print(f"Step 1: Initialize {n_grasshoppers} grasshoppers")

    # ====== Step 2: Initialize parameters ======
    c_max = 1.0
    c_min = 0.00001

    if verbose:
        print(f"Step 2: c_max={c_max}, c_min={c_min}, max_iter={max_iter}")

    # ====== Step 3: Calculate fitness ======
    fitness = np.array([fitness_func(g) for g in grasshoppers])

    if verbose:
        print(f"Step 3: Calculate initial fitness")

    # ====== Step 4: T = best search agent ======
    best_idx = np.argmin(fitness)
    target = grasshoppers[best_idx].copy()
    target_fitness = fitness[best_idx]

    if verbose:
        print(f"Step 4: Initial Target fitness = {target_fitness:.8f}")
        print("="*60)

    convergence = [target_fitness]

    # ====== Step 5: Main loop ======
    for iteration in range(max_iter):

        # Update c using Eq. (2.8)
        c = eq_2_8_adaptive_coefficient(iteration, max_iter, c_max, c_min)

        # Update each search agent
        new_positions = np.zeros_like(grasshoppers)

        for i in range(n_grasshoppers):
            # Update position by Eq. (2.7)
            new_positions[i] = eq_2_7_position_update(
                grasshopper_i=grasshoppers[i],
                all_grasshoppers=grasshoppers,
                i=i,
                target=target,
                c=c,
                lower_bound=lower_bound,
                upper_bound=upper_bound
            )

        # Update grasshoppers
        grasshoppers = new_positions.copy()

        # Evaluate fitness
        fitness = np.array([fitness_func(g) for g in grasshoppers])

        # Update T if there is a better solution
        best_idx = np.argmin(fitness)
        if fitness[best_idx] < target_fitness:
            target = grasshoppers[best_idx].copy()
            target_fitness = fitness[best_idx]

        convergence.append(target_fitness)

        # Progress report
        if verbose and (iteration + 1) % (max_iter // 10) == 0:
            print(f"Iteration {iteration+1:4d}: c={c:.6f} (Eq.2.8), Best={target_fitness:.8f}")

    # ====== Step 6: Return T ======
    if verbose:
        print("="*60)
        print(f"Step 6: Return Target")
        print(f"  Position: {target}")
        print(f"  Fitness:  {target_fitness:.8f}")
        print("="*60)

    return target, target_fitness, convergence


# ============================================================================
# Test Functions
# ============================================================================

def sphere(x):
    """f(x) = Σ(x_i²), minimum = 0 at origin"""
    return np.sum(x ** 2)


def custom_function(x):
    """f(x) = x₀² - x₀ + x₁² - 0.5x₁, minimum = -0.3125 at [0.5, 0.25]"""
    return x[0]**2 - x[0] + x[1]**2 - 0.5*x[1]


# ============================================================================
# Demo: แสดงการทำงานของแต่ละสมการ
# ============================================================================

def demo_equations():
    """สาธิตการทำงานของแต่ละสมการ"""

    print("\n" + "="*70)
    print("DEMO: แสดงการทำงานของแต่ละสมการใน GOA")
    print("="*70)

    # Demo Eq. 2.3
    print("\n[Eq. 2.3] Social Force Function: s(r) = f×e^(-r/l) - e^(-r)")
    print("-"*50)
    print(f"{'r':<10} {'s(r)':<15} {'ความหมาย'}")
    for r in [0.5, 1.0, 2.0, 2.079, 3.0, 4.0]:
        s = eq_2_3_social_force(r)
        meaning = "ผลัก" if s < 0 else ("ดึงดูด" if s > 0.001 else "สบาย")
        print(f"{r:<10.3f} {s:<15.6f} {meaning}")

    # Demo Eq. 2.8
    print("\n[Eq. 2.8] Adaptive Coefficient: c = c_max - iter×(c_max-c_min)/max_iter")
    print("-"*50)
    print(f"{'Iteration':<15} {'c':<15} {'พฤติกรรม'}")
    for it in [0, 100, 250, 400, 500]:
        c = eq_2_8_adaptive_coefficient(it, 500)
        behavior = "Exploration" if c > 0.5 else "Exploitation"
        print(f"{it:<15} {c:<15.6f} {behavior}")

    # Demo Eq. 2.7 (full algorithm)
    print("\n[Eq. 2.7] Position Update - Full Algorithm Test")
    print("-"*50)
    print("ทดสอบกับ f(x) = x₀² - x₀ + x₁² - 0.5x₁")
    print("คำตอบที่ถูกต้อง: x=[0.5, 0.25], f(x)=-0.3125")
    print()

    best_pos, best_fit, _ = GOA_algorithm(
        fitness_func=custom_function,
        n_variables=2,
        lower_bound=[0, 0],
        upper_bound=[1, 1],
        n_grasshoppers=30,
        max_iter=100,
        verbose=True
    )

    print(f"\nผลลัพธ์:")
    print(f"  GOA หาได้: x={best_pos}, f(x)={best_fit:.8f}")
    print(f"  คำตอบจริง: x=[0.5, 0.25], f(x)=-0.3125")
    print(f"  Error: {abs(best_fit - (-0.3125)):.10f}")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║     GOA - แบ่งตามสมการใน Paper                                    ║
    ╠═══════════════════════════════════════════════════════════════════╣
    ║  Eq. 2.3: s(r) = f×e^(-r/l) - e^(-r)     Social Force Function   ║
    ║  Eq. 2.7: X_i = c×(Σ...) + Target        Position Update         ║
    ║  Eq. 2.8: c = c_max - iter×(...)         Adaptive Coefficient    ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    demo_equations()

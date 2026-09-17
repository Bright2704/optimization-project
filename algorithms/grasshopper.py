"""
Grasshopper Optimisation Algorithm (GOA)
========================================
Algorithm ที่จำลองพฤติกรรมการรวมฝูงของตั๊กแตน

หลักการ (จาก Saremi et al., 2017):
1. Social Force: s(r) = f*exp(-r/l) - exp(-r)
   - ระยะใกล้: ผลักกัน (repulsion)
   - ระยะไกล: ดึงดูด (attraction)

2. Position Update: X_i = c * [sum of social interactions] + Target
   - c: ค่าที่ลดลงตาม iteration (exploration -> exploitation)
   - Target: ตำแหน่งที่ดีที่สุดที่หาได้

3. Adaptive c: c = c_max - iter * (c_max - c_min) / max_iter
   - เริ่มต้น c สูง: สำรวจกว้าง (exploration)
   - ท้าย c ต่ำ: ค้นหาละเอียด (exploitation)
"""

import numpy as np


def grasshopper_optimization(
    fitness_func,       # ฟังก์ชันที่ต้องการ minimize
    n_variables,        # จำนวนตัวแปร (มิติ)
    lower_bound,        # ขอบเขตล่าง
    upper_bound,        # ขอบเขตบน
    n_grasshoppers=30,  # จำนวนตั๊กแตน
    max_iter=100,       # จำนวน iterations
    c_max=1.0,          # ค่า c สูงสุด
    c_min=0.00001,      # ค่า c ต่ำสุด
    f=0.5,              # intensity of attraction
    l=1.5,              # attractive length scale
    seed=None,          # random seed
    track_positions=False  # เก็บประวัติตำแหน่งทุก agent (สำหรับ animation)
):
    """
    Grasshopper Optimisation Algorithm

    Returns:
        best_position: ตำแหน่งที่ดีที่สุด
        best_fitness: ค่า fitness ที่ดีที่สุด
        history: ประวัติค่า fitness ที่ดีที่สุดในแต่ละ iteration
        positions_history: (optional) ตำแหน่งของทุก agent ในแต่ละ iteration
    """
    if seed is not None:
        np.random.seed(seed)

    lb = np.array(lower_bound)
    ub = np.array(upper_bound)

    # === Social Force Function ===
    def social_force(r):
        """s(r) = f * exp(-r/l) - exp(-r)"""
        return f * np.exp(-r / l) - np.exp(-r)

    # === Step 1: Initialize Population ===
    grasshoppers = np.random.uniform(lb, ub, size=(n_grasshoppers, n_variables))

    # หา Target (ตัวที่ดีที่สุด)
    fitness_values = np.array([fitness_func(g) for g in grasshoppers])
    best_idx = np.argmin(fitness_values)
    target = grasshoppers[best_idx].copy()
    target_fitness = fitness_values[best_idx]

    history = [target_fitness]
    positions_history = []  # สำหรับ animation

    # บันทึกตำแหน่งเริ่มต้น
    if track_positions:
        positions_history.append(grasshoppers.copy())

    # === Step 2: Main Loop ===
    for iteration in range(max_iter):

        # --- 2.1 คำนวณ c (Adaptive Coefficient) ---
        # c ลดลงจาก c_max ไป c_min ตาม iteration
        c = c_max - iteration * (c_max - c_min) / max_iter

        # --- 2.2 Update ตำแหน่งของแต่ละตั๊กแตน ---
        new_positions = np.zeros_like(grasshoppers)

        for i in range(n_grasshoppers):
            # คำนวณ Social Interaction (S)
            S = np.zeros(n_variables)

            for j in range(n_grasshoppers):
                if i != j:
                    # ระยะห่าง
                    diff = grasshoppers[j] - grasshoppers[i]
                    distance = np.linalg.norm(diff)

                    if distance < 1e-10:
                        continue

                    # Normalize distance to [1, 4]
                    r_norm = 1 + (distance / np.linalg.norm(ub - lb)) * 3
                    r_norm = np.clip(r_norm, 1, 4)

                    # Social force
                    s_val = social_force(r_norm)

                    # Direction (unit vector)
                    direction = diff / distance

                    # Accumulate: c * (ub - lb) / 2 * s * direction
                    S += c * ((ub - lb) / 2) * s_val * direction

            # --- Position Update ---
            # X_i = c * S + Target
            new_positions[i] = c * S + target

            # ตรวจสอบขอบเขต
            new_positions[i] = np.clip(new_positions[i], lb, ub)

        # Update population
        grasshoppers = new_positions.copy()

        # --- 2.3 Update Target ---
        fitness_values = np.array([fitness_func(g) for g in grasshoppers])
        best_idx = np.argmin(fitness_values)

        if fitness_values[best_idx] < target_fitness:
            target = grasshoppers[best_idx].copy()
            target_fitness = fitness_values[best_idx]

        history.append(target_fitness)

        # บันทึกตำแหน่งทุก agent (สำหรับ animation)
        if track_positions:
            positions_history.append(grasshoppers.copy())

    if track_positions:
        return target, target_fitness, history, positions_history
    return target, target_fitness, history


# ==========================================
# ตัวอย่างการใช้งาน
# ==========================================
if __name__ == "__main__":
    def sphere(x):
        return np.sum(x**2)

    pos, fit, hist = grasshopper_optimization(
        fitness_func=sphere,
        n_variables=2,
        lower_bound=[-5, -5],
        upper_bound=[5, 5],
        n_grasshoppers=30,
        max_iter=100,
        seed=42
    )

    print("=== Grasshopper Optimisation Algorithm ===")
    print(f"Best position: {pos}")
    print(f"Best fitness:  {fit:.8f}")
    print(f"True minimum:  0 at [0, 0]")

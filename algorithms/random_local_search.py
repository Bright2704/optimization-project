"""
Random Local Search (RLS)
=========================
Algorithm ง่ายที่สุด: สุ่มเปลี่ยนตำแหน่งเล็กน้อย ถ้าดีกว่าเดิมก็รับ

หลักการ:
1. สร้าง agents สุ่มในพื้นที่
2. แต่ละ iteration: สุ่มขยับตำแหน่งเล็กน้อย
3. ถ้าตำแหน่งใหม่ดีกว่า (fitness ต่ำกว่า) ก็รับ
4. ทำซ้ำจนครบ iterations
"""

import numpy as np


def random_local_search(
    fitness_func,      # ฟังก์ชันที่ต้องการ minimize
    n_variables,       # จำนวนตัวแปร (มิติ)
    lower_bound,       # ขอบเขตล่าง
    upper_bound,       # ขอบเขตบน
    n_agents=30,       # จำนวน agents
    max_iter=100,      # จำนวน iterations
    step_size=0.1,     # ขนาดการขยับ (std ของ normal distribution)
    seed=None,         # random seed สำหรับทำซ้ำได้
    track_positions=False  # เก็บประวัติตำแหน่งทุก agent (สำหรับ animation)
):
    """
    Random Local Search Algorithm

    Returns:
        best_position: ตำแหน่งที่ดีที่สุด
        best_fitness: ค่า fitness ที่ดีที่สุด
        history: ประวัติค่า fitness ที่ดีที่สุดในแต่ละ iteration
        positions_history: (optional) ตำแหน่งของทุก agent ในแต่ละ iteration
    """
    # ตั้งค่า random seed
    if seed is not None:
        np.random.seed(seed)

    # แปลงเป็น numpy array
    lb = np.array(lower_bound)
    ub = np.array(upper_bound)

    # === Step 1: Initialize - สร้าง agents สุ่ม ===
    agents = np.random.uniform(lb, ub, size=(n_agents, n_variables))

    # เก็บประวัติ
    history = []
    positions_history = []  # สำหรับ animation

    # บันทึกตำแหน่งเริ่มต้น
    if track_positions:
        positions_history.append(agents.copy())

    # === Step 2: Main Loop ===
    for iteration in range(max_iter):
        for i in range(n_agents):
            # สร้างการเปลี่ยนแปลงตำแหน่งแบบสุ่ม (Normal distribution)
            delta = np.random.normal(0, step_size, size=n_variables)

            # คำนวณตำแหน่งใหม่
            old_pos = agents[i]
            new_pos = old_pos + delta

            # ตรวจสอบขอบเขต (clip)
            new_pos = np.clip(new_pos, lb, ub)

            # === เปรียบเทียบ fitness ===
            # ถ้าตำแหน่งใหม่ดีกว่า (ค่าน้อยกว่า) ก็รับ
            if fitness_func(new_pos) <= fitness_func(old_pos):
                agents[i] = new_pos

        # หาค่าที่ดีที่สุดใน iteration นี้
        fitness_values = np.array([fitness_func(a) for a in agents])
        best_idx = np.argmin(fitness_values)
        history.append(fitness_values[best_idx])

        # บันทึกตำแหน่งทุก agent (สำหรับ animation)
        if track_positions:
            positions_history.append(agents.copy())

    # === Step 3: Return ผลลัพธ์ ===
    fitness_values = np.array([fitness_func(a) for a in agents])
    best_idx = np.argmin(fitness_values)
    best_position = agents[best_idx]
    best_fitness = fitness_values[best_idx]

    if track_positions:
        return best_position, best_fitness, history, positions_history
    return best_position, best_fitness, history


# ==========================================
# ตัวอย่างการใช้งาน
# ==========================================
if __name__ == "__main__":
    # ฟังก์ชันทดสอบง่ายๆ: Sphere function
    def sphere(x):
        return np.sum(x**2)

    # รัน algorithm
    pos, fit, hist = random_local_search(
        fitness_func=sphere,
        n_variables=2,
        lower_bound=[-5, -5],
        upper_bound=[5, 5],
        n_agents=20,
        max_iter=50,
        step_size=0.5,
        seed=42
    )

    print("=== Random Local Search ===")
    print(f"Best position: {pos}")
    print(f"Best fitness:  {fit:.8f}")
    print(f"True minimum:  0 at [0, 0]")

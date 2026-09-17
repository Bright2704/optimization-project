"""
=============================================================================
    Simple Animation for Optimization Algorithms
    =============================================
    ไฟล์เดียว ง่ายๆ สำหรับนำเสนอ

    วิธีใช้: python animation_simple.py
=============================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# =============================================================================
# 1. Objective Functions (ฟังก์ชันที่ต้องการหาค่าต่ำสุด)
# =============================================================================

def sphere(x, y):
    """Sphere Function: f(x,y) = x² + y²
    ค่าต่ำสุด = 0 ที่จุด (0, 0)
    """
    return x**2 + y**2

def rosenbrock(x, y):
    """Rosenbrock Function: f(x,y) = 100(y - x²)² + (x - 1)²
    ค่าต่ำสุด = 0 ที่จุด (1, 1)
    """
    return 100 * (y - x**2)**2 + (x - 1)**2

# =============================================================================
# 2. Grasshopper Optimization Algorithm (GOA) - แบบง่าย
# =============================================================================

def run_goa_simple(func, n_agents=20, max_iter=50, bounds=(-5, 5)):
    """
    GOA Algorithm แบบง่าย

    Parameters:
        func: ฟังก์ชันที่ต้องการ minimize
        n_agents: จำนวน agents (ตั๊กแตน)
        max_iter: จำนวนรอบ
        bounds: ขอบเขตการค้นหา

    Returns:
        history: list ของตำแหน่ง agents ในแต่ละรอบ
        best_history: list ของตำแหน่งที่ดีที่สุดในแต่ละรอบ
    """

    # --- Step 1: สร้าง agents แบบสุ่ม ---
    agents_x = np.random.uniform(bounds[0], bounds[1], n_agents)
    agents_y = np.random.uniform(bounds[0], bounds[1], n_agents)

    # หาตัวที่ดีที่สุด
    fitness = func(agents_x, agents_y)
    best_idx = np.argmin(fitness)
    target_x, target_y = agents_x[best_idx], agents_y[best_idx]

    # เก็บประวัติ
    history = [(agents_x.copy(), agents_y.copy())]
    best_history = [(target_x, target_y)]

    # --- Step 2: Loop หลัก ---
    for iteration in range(max_iter):

        # c ลดลงจาก 1 ไป 0.0001 (exploration -> exploitation)
        c = 1 - iteration * (1 - 0.0001) / max_iter

        # อัพเดทตำแหน่งแต่ละ agent
        new_x = np.zeros(n_agents)
        new_y = np.zeros(n_agents)

        for i in range(n_agents):
            # คำนวณแรงจาก agents ตัวอื่น
            force_x, force_y = 0, 0

            for j in range(n_agents):
                if i != j:
                    # ระยะห่าง
                    dx = agents_x[j] - agents_x[i]
                    dy = agents_y[j] - agents_y[i]
                    dist = np.sqrt(dx**2 + dy**2) + 0.0001

                    # Social force: s(r) = 0.5*exp(-r/1.5) - exp(-r)
                    r = min(max(dist, 1), 4)  # normalize to [1, 4]
                    s = 0.5 * np.exp(-r / 1.5) - np.exp(-r)

                    # สะสมแรง
                    force_x += s * dx / dist
                    force_y += s * dy / dist

            # ตำแหน่งใหม่ = c * แรง + target
            new_x[i] = c * force_x + target_x
            new_y[i] = c * force_y + target_y

            # ตรวจสอบขอบเขต
            new_x[i] = np.clip(new_x[i], bounds[0], bounds[1])
            new_y[i] = np.clip(new_y[i], bounds[0], bounds[1])

        # อัพเดท agents
        agents_x, agents_y = new_x, new_y

        # อัพเดท target (ถ้าเจอตัวที่ดีกว่า)
        fitness = func(agents_x, agents_y)
        best_idx = np.argmin(fitness)
        if fitness[best_idx] < func(target_x, target_y):
            target_x, target_y = agents_x[best_idx], agents_y[best_idx]

        # เก็บประวัติ
        history.append((agents_x.copy(), agents_y.copy()))
        best_history.append((target_x, target_y))

    return history, best_history

# =============================================================================
# 3. สร้าง Animation
# =============================================================================

def create_animation(func, func_name, bounds, optimal_point, n_agents=20, max_iter=50):
    """สร้าง Animation แสดงการทำงานของ GOA"""

    print(f"กำลังรัน GOA บน {func_name}...")
    history, best_history = run_goa_simple(func, n_agents, max_iter, bounds)
    print(f"เสร็จแล้ว! Best fitness = {func(*best_history[-1]):.6f}")

    # --- สร้าง Figure ---
    fig, ax = plt.subplots(figsize=(10, 8))

    # วาด contour (พื้นหลัง)
    x = np.linspace(bounds[0], bounds[1], 100)
    y = np.linspace(bounds[0], bounds[1], 100)
    X, Y = np.meshgrid(x, y)
    Z = func(X, Y)

    contour = ax.contourf(X, Y, Z, levels=30, cmap='Blues', alpha=0.6)
    plt.colorbar(contour, ax=ax, label='Fitness')

    # จุดเป้าหมายที่แท้จริง
    ax.plot(optimal_point[0], optimal_point[1], 'g*', markersize=20,
            label=f'Global Optimum {optimal_point}', zorder=10)

    # สร้าง scatter plot สำหรับ agents
    agents_scatter = ax.scatter([], [], c='red', s=100, label='Agents', zorder=5)
    best_scatter = ax.scatter([], [], c='yellow', s=200, marker='*',
                               edgecolors='orange', linewidths=2,
                               label='Current Best', zorder=6)

    # Title และ labels
    title = ax.set_title(f'{func_name} - Iteration 0/{max_iter}', fontsize=14)
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.legend(loc='upper right')
    ax.set_xlim(bounds[0], bounds[1])
    ax.set_ylim(bounds[0], bounds[1])
    ax.grid(True, alpha=0.3)

    # --- Animation Function ---
    def update(frame):
        agents_x, agents_y = history[frame]
        best_x, best_y = best_history[frame]
        fitness = func(best_x, best_y)

        # อัพเดท scatter plots
        agents_scatter.set_offsets(np.c_[agents_x, agents_y])
        best_scatter.set_offsets([[best_x, best_y]])

        # อัพเดท title
        title.set_text(f'{func_name} - Iteration {frame}/{max_iter}\n'
                      f'Best: ({best_x:.4f}, {best_y:.4f}) | Fitness: {fitness:.6f}')

        return agents_scatter, best_scatter, title

    # สร้าง animation
    anim = FuncAnimation(fig, update, frames=len(history),
                        interval=200, blit=False, repeat=True)

    plt.tight_layout()
    return fig, anim

# =============================================================================
# 4. Main - รันโปรแกรม
# =============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("  GOA Animation - Simple Version")
    print("=" * 50)
    print()
    print("เลือก Function:")
    print("  1. Sphere (ง่าย) - optimal at (0, 0)")
    print("  2. Rosenbrock (ยาก) - optimal at (1, 1)")
    print()

    choice = input("เลือก (1 หรือ 2): ").strip()

    if choice == "2":
        func = rosenbrock
        func_name = "Rosenbrock Function"
        bounds = (-2, 2)
        optimal = (1, 1)
    else:
        func = sphere
        func_name = "Sphere Function"
        bounds = (-5, 5)
        optimal = (0, 0)

    print()
    fig, anim = create_animation(func, func_name, bounds, optimal,
                                  n_agents=20, max_iter=50)

    print()
    print("กำลังแสดง Animation...")
    print("  - จุดแดง = Agents (กำลังค้นหา)")
    print("  - ดาวเหลือง = ตำแหน่งที่ดีที่สุดในรอบนั้น")
    print("  - ดาวเขียว = คำตอบที่ถูกต้อง")
    print()
    print("ปิดหน้าต่างเพื่อจบโปรแกรม")

    plt.show()

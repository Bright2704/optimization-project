"""
=============================================================================
    Simple Snapshots for Presentation
    ==================================
    สร้างภาพ snapshots หลายๆ iteration สำหรับใส่ใน slides

    วิธีใช้: python snapshots_simple.py
    ผลลัพธ์: ไฟล์ภาพใน folder "snapshots/"
=============================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# =============================================================================
# 1. Objective Functions
# =============================================================================

def sphere(x, y):
    """Sphere: f(x,y) = x² + y², optimal at (0,0)"""
    return x**2 + y**2

def rosenbrock(x, y):
    """Rosenbrock: f(x,y) = 100(y-x²)² + (x-1)², optimal at (1,1)"""
    return 100 * (y - x**2)**2 + (x - 1)**2

# =============================================================================
# 2. GOA Algorithm (แบบง่าย)
# =============================================================================

def run_goa(func, n_agents=20, max_iter=50, bounds=(-5, 5)):
    """รัน GOA และเก็บประวัติ"""

    # สร้าง agents สุ่ม
    agents_x = np.random.uniform(bounds[0], bounds[1], n_agents)
    agents_y = np.random.uniform(bounds[0], bounds[1], n_agents)

    # หา target (ตัวที่ดีที่สุด)
    fitness = func(agents_x, agents_y)
    best_idx = np.argmin(fitness)
    target_x, target_y = agents_x[best_idx], agents_y[best_idx]

    # เก็บประวัติ
    history = [(agents_x.copy(), agents_y.copy(), target_x, target_y)]

    # Main loop
    for iteration in range(max_iter):
        c = 1 - iteration * (1 - 0.0001) / max_iter

        new_x = np.zeros(n_agents)
        new_y = np.zeros(n_agents)

        for i in range(n_agents):
            force_x, force_y = 0, 0
            for j in range(n_agents):
                if i != j:
                    dx = agents_x[j] - agents_x[i]
                    dy = agents_y[j] - agents_y[i]
                    dist = np.sqrt(dx**2 + dy**2) + 0.0001
                    r = min(max(dist, 1), 4)
                    s = 0.5 * np.exp(-r / 1.5) - np.exp(-r)
                    force_x += s * dx / dist
                    force_y += s * dy / dist

            new_x[i] = np.clip(c * force_x + target_x, bounds[0], bounds[1])
            new_y[i] = np.clip(c * force_y + target_y, bounds[0], bounds[1])

        agents_x, agents_y = new_x, new_y

        fitness = func(agents_x, agents_y)
        best_idx = np.argmin(fitness)
        if fitness[best_idx] < func(target_x, target_y):
            target_x, target_y = agents_x[best_idx], agents_y[best_idx]

        history.append((agents_x.copy(), agents_y.copy(), target_x, target_y))

    return history

# =============================================================================
# 3. สร้าง Snapshot 1 รูป
# =============================================================================

def draw_snapshot(ax, func, history, frame, bounds, optimal, title_prefix=""):
    """วาด snapshot ของ iteration ที่กำหนด"""

    agents_x, agents_y, best_x, best_y = history[frame]
    fitness = func(best_x, best_y)

    # วาด contour
    x = np.linspace(bounds[0], bounds[1], 80)
    y = np.linspace(bounds[0], bounds[1], 80)
    X, Y = np.meshgrid(x, y)
    Z = func(X, Y)

    ax.contourf(X, Y, Z, levels=20, cmap='Blues', alpha=0.5)

    # วาด agents (จุดแดง)
    ax.scatter(agents_x, agents_y, c='red', s=80, label='Agents', zorder=5)

    # วาด best (ดาวเหลือง)
    ax.scatter(best_x, best_y, c='yellow', s=200, marker='*',
               edgecolors='orange', linewidths=2, label='Best', zorder=6)

    # วาด optimal (ดาวเขียว)
    ax.scatter(optimal[0], optimal[1], c='lime', s=300, marker='*',
               edgecolors='green', linewidths=2, label='Target', zorder=7)

    # ตกแต่ง
    ax.set_xlim(bounds[0], bounds[1])
    ax.set_ylim(bounds[0], bounds[1])
    ax.set_xlabel('X', fontsize=11)
    ax.set_ylabel('Y', fontsize=11)
    ax.grid(True, alpha=0.3)

    ax.set_title(f'{title_prefix}Iteration {frame}\n'
                f'Best: ({best_x:.3f}, {best_y:.3f})\n'
                f'Fitness: {fitness:.6f}', fontsize=11)

# =============================================================================
# 4. สร้างภาพ Snapshots หลายๆ รูป
# =============================================================================

def create_snapshots(func, func_name, bounds, optimal, n_agents=20, max_iter=50):
    """สร้าง snapshot images"""

    print(f"กำลังรัน GOA บน {func_name}...")
    np.random.seed(42)  # ให้ผลลัพธ์เหมือนกันทุกครั้ง
    history = run_goa(func, n_agents, max_iter, bounds)

    # สร้าง folder
    output_dir = "snapshots"
    os.makedirs(output_dir, exist_ok=True)

    # เลือก iterations ที่จะ snapshot
    total = len(history)
    frames = [0, total//4, total//2, 3*total//4, total-1]
    frames = sorted(set(frames))

    print(f"สร้าง snapshots สำหรับ iterations: {frames}")

    # --- รูปที่ 1: รวมทุก snapshots ในภาพเดียว ---
    fig, axes = plt.subplots(1, len(frames), figsize=(4*len(frames), 4))

    for i, frame in enumerate(frames):
        draw_snapshot(axes[i], func, history, frame, bounds, optimal)

    fig.suptitle(f'GOA on {func_name} - Snapshots', fontsize=14, fontweight='bold')
    plt.tight_layout()

    filename = f"{output_dir}/{func_name.lower().replace(' ', '_')}_all.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"  บันทึก: {filename}")
    plt.close()

    # --- รูปที่ 2-6: แต่ละ snapshot แยกไฟล์ ---
    for frame in frames:
        fig, ax = plt.subplots(figsize=(6, 5))
        draw_snapshot(ax, func, history, frame, bounds, optimal, f"{func_name}\n")
        ax.legend(loc='upper right')

        filename = f"{output_dir}/{func_name.lower().replace(' ', '_')}_iter{frame:03d}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"  บันทึก: {filename}")
        plt.close()

    # แสดงผลลัพธ์สุดท้าย
    final_fitness = func(history[-1][2], history[-1][3])
    print(f"\nผลลัพธ์สุดท้าย:")
    print(f"  Position: ({history[-1][2]:.6f}, {history[-1][3]:.6f})")
    print(f"  Fitness: {final_fitness:.8f}")

# =============================================================================
# 5. Main
# =============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("  Snapshot Generator for Presentation")
    print("=" * 50)
    print()

    # สร้าง snapshots สำหรับ Sphere
    print("[1/2] Sphere Function")
    print("-" * 30)
    create_snapshots(sphere, "Sphere Function", (-5, 5), (0, 0))
    print()

    # สร้าง snapshots สำหรับ Rosenbrock
    print("[2/2] Rosenbrock Function")
    print("-" * 30)
    create_snapshots(rosenbrock, "Rosenbrock Function", (-2, 2), (1, 1))
    print()

    print("=" * 50)
    print("  เสร็จแล้ว! ดูภาพใน folder 'snapshots/'")
    print("=" * 50)

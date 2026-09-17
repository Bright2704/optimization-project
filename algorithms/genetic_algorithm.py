"""
Genetic Algorithm (GA)
======================
Algorithm ที่จำลองการวิวัฒนาการทางพันธุกรรม

หลักการ (จาก PDF l9-11.pdf):
1. สร้าง Population เริ่มต้น
2. Selection - เลือก chromosomes ที่ fitness ดี (Roulette Wheel)
3. Crossover - แลกเปลี่ยน genes ระหว่าง parents
4. Mutation - เปลี่ยนแปลง genes แบบสุ่ม
5. ทำซ้ำจนครบ generations

หมายเหตุ: ใช้ Real-Number GA (ไม่ใช้ binary encoding)
"""

import numpy as np


def genetic_algorithm(
    fitness_func,       # ฟังก์ชันที่ต้องการ minimize
    n_variables,        # จำนวนตัวแปร (มิติ)
    lower_bound,        # ขอบเขตล่าง
    upper_bound,        # ขอบเขตบน
    pop_size=30,        # ขนาด population
    max_iter=100,       # จำนวน generations
    crossover_rate=0.8, # อัตราการ crossover (p_c)
    mutation_rate=0.1,  # อัตราการ mutation (p_m)
    seed=None,          # random seed
    track_positions=False  # เก็บประวัติตำแหน่งทุก agent (สำหรับ animation)
):
    """
    Genetic Algorithm (Real-Number Version)

    Returns:
        best_position: ตำแหน่งที่ดีที่สุด
        best_fitness: ค่า fitness ที่ดีที่สุด
        history: ประวัติค่า fitness ที่ดีที่สุดในแต่ละ generation
        positions_history: (optional) ตำแหน่งของทุก agent ในแต่ละ generation
    """
    if seed is not None:
        np.random.seed(seed)

    lb = np.array(lower_bound)
    ub = np.array(upper_bound)

    # === Step 1: Initialize Population ===
    # สร้าง chromosomes สุ่มใน search space
    population = np.random.uniform(lb, ub, size=(pop_size, n_variables))

    # หา global best
    fitness_values = np.array([fitness_func(ind) for ind in population])
    best_idx = np.argmin(fitness_values)
    global_best = population[best_idx].copy()
    global_best_fitness = fitness_values[best_idx]

    history = [global_best_fitness]
    positions_history = []  # สำหรับ animation

    # บันทึกตำแหน่งเริ่มต้น
    if track_positions:
        positions_history.append(population.copy())

    # === Step 2: Main Loop (Generations) ===
    for generation in range(max_iter):

        # --- 2.1 Selection (Roulette Wheel) ---
        # แปลง fitness สำหรับ minimization (ค่าน้อย = ดี = ความน่าจะเป็นสูง)
        # ใช้ inverse: ยิ่งค่าน้อย ยิ่งความน่าจะเป็นสูง
        fitness_values = np.array([fitness_func(ind) for ind in population])

        # แปลงเป็น positive และ inverse
        max_fit = np.max(fitness_values)
        adjusted_fitness = max_fit - fitness_values + 1e-10  # +epsilon กัน division by zero

        # คำนวณความน่าจะเป็น
        total_fitness = np.sum(adjusted_fitness)
        probabilities = adjusted_fitness / total_fitness

        # เลือก parents ด้วย Roulette Wheel
        selected_indices = np.random.choice(
            pop_size, size=pop_size, replace=True, p=probabilities
        )
        mating_pool = population[selected_indices].copy()

        # --- 2.2 Crossover ---
        # จับคู่และแลกเปลี่ยน genes
        new_population = []

        for i in range(0, pop_size, 2):
            parent1 = mating_pool[i]
            parent2 = mating_pool[min(i + 1, pop_size - 1)]

            if np.random.random() < crossover_rate:
                # Arithmetic Crossover: z = α*x + (1-α)*y
                alpha = np.random.random()
                child1 = alpha * parent1 + (1 - alpha) * parent2
                child2 = (1 - alpha) * parent1 + alpha * parent2
            else:
                child1 = parent1.copy()
                child2 = parent2.copy()

            new_population.append(child1)
            if len(new_population) < pop_size:
                new_population.append(child2)

        population = np.array(new_population)

        # --- 2.3 Mutation ---
        # เปลี่ยนแปลง genes แบบสุ่ม
        for i in range(pop_size):
            if np.random.random() < mutation_rate:
                # Gaussian Mutation: เพิ่ม noise
                mutation = np.random.normal(0, 0.1 * (ub - lb), size=n_variables)
                population[i] = population[i] + mutation

        # ตรวจสอบขอบเขต
        population = np.clip(population, lb, ub)

        # --- 2.4 Update Global Best ---
        fitness_values = np.array([fitness_func(ind) for ind in population])
        best_idx = np.argmin(fitness_values)

        if fitness_values[best_idx] < global_best_fitness:
            global_best = population[best_idx].copy()
            global_best_fitness = fitness_values[best_idx]

        history.append(global_best_fitness)

        # บันทึกตำแหน่งทุก agent (สำหรับ animation)
        if track_positions:
            positions_history.append(population.copy())

    if track_positions:
        return global_best, global_best_fitness, history, positions_history
    return global_best, global_best_fitness, history


# ==========================================
# ตัวอย่างการใช้งาน
# ==========================================
if __name__ == "__main__":
    # ฟังก์ชันทดสอบ
    def sphere(x):
        return np.sum(x**2)

    pos, fit, hist = genetic_algorithm(
        fitness_func=sphere,
        n_variables=2,
        lower_bound=[-5, -5],
        upper_bound=[5, 5],
        pop_size=30,
        max_iter=100,
        crossover_rate=0.8,
        mutation_rate=0.1,
        seed=42
    )

    print("=== Genetic Algorithm ===")
    print(f"Best position: {pos}")
    print(f"Best fitness:  {fit:.8f}")
    print(f"True minimum:  0 at [0, 0]")

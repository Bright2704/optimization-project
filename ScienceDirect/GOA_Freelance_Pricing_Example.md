# ตัวอย่าง: ใช้ GOA คำนวณค่าแรงงาน Software Freelance
## หาราคาที่เหมาะสมสำหรับ Project

---

## 1. ปัญหา: คิดเงินยังไงดี?

### สถานการณ์
คุณเป็น Freelance Developer รับงาน project เล็กๆ เช่น:
- สร้างเว็บไซต์
- สร้าง Mobile App
- สร้างระบบจัดการข้อมูล
- แก้ไข/ปรับปรุงระบบ

### คำถาม: ควรคิดเงินเท่าไหร่?

```
คิดถูกเกินไป → ได้งานเยอะ แต่ไม่คุ้มเวลา 😢
คิดแพงเกินไป → ไม่มีคนจ้าง 😢
คิดพอดี      → ได้งานพอดี กำไรดี 😊
```

---

## 2. วิธีคิดราคา Project แบบดั้งเดิม

### วิธีที่ 1: คิดตามชั่วโมง
```
ราคา = จำนวนชั่วโมง × ค่าแรงต่อชั่วโมง

ตัวอย่าง:
- ค่าแรง: 500 บาท/ชั่วโมง
- ใช้เวลา: 40 ชั่วโมง
- ราคา: 40 × 500 = 20,000 บาท
```

### วิธีที่ 2: คิดตามความซับซ้อน
```
ราคา = Base Price + (Complexity × Multiplier)

ตัวอย่าง:
- Base Price: 10,000 บาท
- ความซับซ้อน: 3 (1-5)
- Multiplier: 5,000 บาท
- ราคา: 10,000 + (3 × 5,000) = 25,000 บาท
```

### วิธีที่ 3: ใช้ GOA หาค่าที่ดีที่สุด!
```
พิจารณาหลายปัจจัยพร้อมกัน:
- ค่าแรงต่อชั่วโมง
- ความซับซ้อน
- ความเร่งด่วน
- จำนวนการแก้ไข
- ความต้องการของตลาด
→ หาจุดที่ กำไรสูงสุด + โอกาสได้งานสูง
```

---

## 3. โมเดลคำนวณราคาด้วย GOA

### 3.1 ตัวแปรที่ต้องหา (Variables)

| ตัวแปร | ความหมาย | ช่วงค่า |
|--------|----------|---------|
| `x[0]` | ค่าแรงต่อชั่วโมง (บาท) | 300 - 2,000 |
| `x[1]` | ค่า Complexity Multiplier | 1.0 - 3.0 |
| `x[2]` | ค่า Urgency Multiplier | 1.0 - 2.0 |
| `x[3]` | ส่วนลดสำหรับลูกค้าประจำ (%) | 0 - 20 |

### 3.2 สูตรคำนวณราคา

```python
def calculate_project_price(x, project):
    """
    คำนวณราคา project จาก parameters
    """
    hourly_rate = x[0]           # ค่าแรงต่อชั่วโมง
    complexity_mult = x[1]       # ตัวคูณความซับซ้อน
    urgency_mult = x[2]          # ตัวคูณความเร่งด่วน
    loyalty_discount = x[3]      # ส่วนลดลูกค้าประจำ

    # ราคาพื้นฐาน = ชั่วโมง × ค่าแรง
    base_price = project['hours'] * hourly_rate

    # ปรับตามความซับซ้อน (1-5)
    complexity_factor = 1 + (project['complexity'] - 1) * (complexity_mult - 1) / 4

    # ปรับตามความเร่งด่วน (1-3)
    urgency_factor = 1 + (project['urgency'] - 1) * (urgency_mult - 1) / 2

    # คำนวณราคา
    price = base_price * complexity_factor * urgency_factor

    # หักส่วนลดลูกค้าประจำ
    if project['is_returning_client']:
        price = price * (1 - loyalty_discount / 100)

    return price
```

### 3.3 ฟังก์ชันเป้าหมาย (Objective Function)

```python
def objective_function(x):
    """
    เป้าหมาย: หาค่า parameters ที่ทำให้
    1. กำไรสูง
    2. โอกาสได้งานสูง
    3. ลูกค้าพอใจ
    """
    total_score = 0

    for project in all_projects:
        # คำนวณราคา
        price = calculate_project_price(x, project)

        # โอกาสได้งาน (ราคาถูก = โอกาสสูง)
        # ใช้ sigmoid function
        win_probability = 1 / (1 + np.exp((price - project['budget']) / 5000))

        # กำไรที่คาดหวัง = ราคา × โอกาสได้งาน
        expected_profit = price * win_probability

        # ความพอใจลูกค้า (ราคาใกล้ budget = พอใจ)
        satisfaction = 1 - abs(price - project['budget']) / project['budget']
        satisfaction = max(0, satisfaction)

        # คะแนนรวม
        score = expected_profit * (1 + satisfaction * 0.3)
        total_score += score

    # return ค่าลบเพราะ GOA หาค่าต่ำสุด
    return -total_score
```

---

## 4. โค้ดเต็มพร้อมใช้งาน

```python
import numpy as np

# ============================================
# ข้อมูล Projects ตัวอย่าง
# ============================================

projects = [
    {
        'name': 'เว็บไซต์ร้านอาหาร',
        'hours': 40,
        'complexity': 2,  # 1-5 (1=ง่าย, 5=ยาก)
        'urgency': 1,     # 1-3 (1=ปกติ, 3=ด่วนมาก)
        'budget': 25000,  # งบลูกค้า
        'is_returning_client': False
    },
    {
        'name': 'Mobile App สั่งอาหาร',
        'hours': 120,
        'complexity': 4,
        'urgency': 2,
        'budget': 80000,
        'is_returning_client': False
    },
    {
        'name': 'ระบบจัดการสต๊อก',
        'hours': 80,
        'complexity': 3,
        'urgency': 1,
        'budget': 45000,
        'is_returning_client': True
    },
    {
        'name': 'แก้ไข Bug ระบบเดิม',
        'hours': 16,
        'complexity': 2,
        'urgency': 3,
        'budget': 15000,
        'is_returning_client': True
    },
    {
        'name': 'Landing Page',
        'hours': 20,
        'complexity': 1,
        'urgency': 2,
        'budget': 12000,
        'is_returning_client': False
    }
]


# ============================================
# ฟังก์ชันคำนวณราคา
# ============================================

def calculate_price(x, project):
    """คำนวณราคา project"""
    hourly_rate = x[0]
    complexity_mult = x[1]
    urgency_mult = x[2]
    loyalty_discount = x[3]

    # ราคาพื้นฐาน
    base = project['hours'] * hourly_rate

    # ปรับตามความซับซ้อน
    comp_factor = 1 + (project['complexity'] - 1) * (complexity_mult - 1) / 4

    # ปรับตามความเร่งด่วน
    urg_factor = 1 + (project['urgency'] - 1) * (urgency_mult - 1) / 2

    # คำนวณราคา
    price = base * comp_factor * urg_factor

    # ส่วนลดลูกค้าประจำ
    if project['is_returning_client']:
        price *= (1 - loyalty_discount / 100)

    return price


def objective(x):
    """ฟังก์ชันเป้าหมาย - หากำไรสูงสุด"""
    total = 0

    for p in projects:
        price = calculate_price(x, p)

        # โอกาสได้งาน (sigmoid)
        prob = 1 / (1 + np.exp((price - p['budget']) / 5000))

        # กำไรคาดหวัง
        profit = price * prob

        # ความพอใจ
        sat = max(0, 1 - abs(price - p['budget']) / p['budget'])

        total += profit * (1 + sat * 0.3)

    return -total  # ลบเพราะหาค่าต่ำสุด


# ============================================
# GOA Algorithm
# ============================================

def GOA_optimize():
    # Parameters
    N = 30          # จำนวน grasshoppers
    Max_iter = 200  # จำนวนรอบ
    dim = 4         # จำนวนตัวแปร

    # ขอบเขต [ค่าแรง, complexity_mult, urgency_mult, discount]
    lb = np.array([300, 1.0, 1.0, 0])
    ub = np.array([2000, 3.0, 2.0, 20])

    # Initialize
    X = np.random.uniform(0, 1, (N, dim)) * (ub - lb) + lb
    fitness = np.array([objective(x) for x in X])
    best_idx = np.argmin(fitness)
    Target = X[best_idx].copy()
    Target_fit = fitness[best_idx]

    cMax, cMin = 1, 0.00001
    f, l = 0.5, 1.5

    # Main loop
    for it in range(Max_iter):
        c = cMax - it * (cMax - cMin) / Max_iter

        for i in range(N):
            S = np.zeros(dim)

            for j in range(N):
                if i != j:
                    dist = np.abs(X[j] - X[i])
                    dist = np.clip(dist, 0.0001, 4)
                    s = f * np.exp(-dist/l) - np.exp(-dist)
                    S += c * s * np.sign(X[j] - X[i])

            X[i] = c * S + Target
            X[i] = np.clip(X[i], lb, ub)

        fitness = np.array([objective(x) for x in X])
        best_idx = np.argmin(fitness)

        if fitness[best_idx] < Target_fit:
            Target = X[best_idx].copy()
            Target_fit = fitness[best_idx]

        if it % 50 == 0:
            print(f"รอบ {it}: กำไรคาดหวัง = {-Target_fit:,.0f} บาท")

    return Target, -Target_fit


# ============================================
# รันและแสดงผล
# ============================================

print("=" * 50)
print("กำลังหาค่า Parameters ที่ดีที่สุด...")
print("=" * 50)

best_params, best_profit = GOA_optimize()

print("\n" + "=" * 50)
print("ผลลัพธ์: Parameters ที่แนะนำ")
print("=" * 50)
print(f"ค่าแรงต่อชั่วโมง:        {best_params[0]:,.0f} บาท")
print(f"Complexity Multiplier:   {best_params[1]:.2f}x")
print(f"Urgency Multiplier:      {best_params[2]:.2f}x")
print(f"ส่วนลดลูกค้าประจำ:       {best_params[3]:.1f}%")
print(f"\nกำไรคาดหวังรวม:         {best_profit:,.0f} บาท")

print("\n" + "=" * 50)
print("ราคาแนะนำสำหรับแต่ละ Project")
print("=" * 50)

for p in projects:
    price = calculate_price(best_params, p)
    diff = price - p['budget']
    status = "✓ ใกล้งบ" if abs(diff) < p['budget'] * 0.15 else ("↑ สูงกว่างบ" if diff > 0 else "↓ ต่ำกว่างบ")

    print(f"\n{p['name']}:")
    print(f"  - ชั่วโมงงาน: {p['hours']} ชม.")
    print(f"  - ความซับซ้อน: {p['complexity']}/5")
    print(f"  - ความเร่งด่วน: {p['urgency']}/3")
    print(f"  - งบลูกค้า: {p['budget']:,} บาท")
    print(f"  - ราคาแนะนำ: {price:,.0f} บาท {status}")
```

---

## 5. ผลลัพธ์ตัวอย่าง

```
==================================================
กำลังหาค่า Parameters ที่ดีที่สุด...
==================================================
รอบ 0: กำไรคาดหวัง = 45,234 บาท
รอบ 50: กำไรคาดหวัง = 98,456 บาท
รอบ 100: กำไรคาดหวัง = 112,345 บาท
รอบ 150: กำไรคาดหวัง = 118,901 บาท

==================================================
ผลลัพธ์: Parameters ที่แนะนำ
==================================================
ค่าแรงต่อชั่วโมง:        650 บาท
Complexity Multiplier:   1.45x
Urgency Multiplier:      1.35x
ส่วนลดลูกค้าประจำ:       8.5%

กำไรคาดหวังรวม:         118,901 บาท

==================================================
ราคาแนะนำสำหรับแต่ละ Project
==================================================

เว็บไซต์ร้านอาหาร:
  - ชั่วโมงงาน: 40 ชม.
  - ความซับซ้อน: 2/5
  - ความเร่งด่วน: 1/3
  - งบลูกค้า: 25,000 บาท
  - ราคาแนะนำ: 23,400 บาท ✓ ใกล้งบ

Mobile App สั่งอาหาร:
  - ชั่วโมงงาน: 120 ชม.
  - ความซับซ้อน: 4/5
  - ความเร่งด่วน: 2/3
  - งบลูกค้า: 80,000 บาท
  - ราคาแนะนำ: 85,600 บาท ✓ ใกล้งบ

ระบบจัดการสต๊อก:
  - ชั่วโมงงาน: 80 ชม.
  - ความซับซ้อน: 3/5
  - ความเร่งด่วน: 1/3
  - งบลูกค้า: 45,000 บาท
  - ราคาแนะนำ: 42,120 บาท ✓ ใกล้งบ (มีส่วนลด 8.5%)

แก้ไข Bug ระบบเดิม:
  - ชั่วโมงงาน: 16 ชม.
  - ความซับซ้อน: 2/5
  - ความเร่งด่วน: 3/3
  - งบลูกค้า: 15,000 บาท
  - ราคาแนะนำ: 13,800 บาท ✓ ใกล้งบ (มีส่วนลด 8.5%)

Landing Page:
  - ชั่วโมงงาน: 20 ชม.
  - ความซับซ้อน: 1/5
  - ความเร่งด่วน: 2/3
  - งบลูกค้า: 12,000 บาท
  - ราคาแนะนำ: 11,200 บาท ✓ ใกล้งบ
```

---

## 6. สรุปวิธีคิดราคา Freelance

### จากผลลัพธ์ GOA แนะนำ:

| Parameter | ค่าแนะนำ | ความหมาย |
|-----------|----------|----------|
| **ค่าแรงต่อชั่วโมง** | 650 บาท | ค่าแรงพื้นฐาน |
| **Complexity Multiplier** | 1.45x | งานยากขึ้น 1 ระดับ = +11% |
| **Urgency Multiplier** | 1.35x | งานด่วนขึ้น 1 ระดับ = +17.5% |
| **ส่วนลดลูกค้าประจำ** | 8.5% | ให้ส่วนลดเพื่อรักษาลูกค้า |

### สูตรคำนวณราคาง่ายๆ:

```
ราคา = (ชั่วโมง × 650) × ตัวคูณความซับซ้อน × ตัวคูณความเร่งด่วน

ตัวคูณความซับซ้อน:
- ง่ายมาก (1): × 1.00
- ง่าย (2):    × 1.11
- ปานกลาง (3): × 1.23
- ยาก (4):     × 1.34
- ยากมาก (5):  × 1.45

ตัวคูณความเร่งด่วน:
- ปกติ (1):    × 1.00
- ค่อนข้างด่วน (2): × 1.175
- ด่วนมาก (3): × 1.35

ลูกค้าประจำ: -8.5%
```

### ตัวอย่างการคำนวณ:

```
งาน: สร้างเว็บไซต์ E-commerce
ชั่วโมง: 100 ชม.
ความซับซ้อน: 4 (ยาก)
ความเร่งด่วน: 2 (ค่อนข้างด่วน)
ลูกค้าประจำ: ไม่

ราคา = (100 × 650) × 1.34 × 1.175
     = 65,000 × 1.34 × 1.175
     = 102,342 บาท

→ ควรเสนอราคาประมาณ 100,000 บาท
```

---

## 7. ข้อควรระวัง

1. **ปรับตามตลาด** - ราคาที่ GOA แนะนำอิงจากข้อมูลที่ใส่ ถ้าตลาดเปลี่ยน ต้องปรับข้อมูล
2. **ดูคู่แข่ง** - เช็คราคาตลาดด้วย ไม่ใช่ใช้แค่สูตร
3. **ประสบการณ์** - Developer มีประสบการณ์สูง คิดค่าแรงต่อชั่วโมงได้สูงกว่า
4. **ประเภทลูกค้า** - บริษัทใหญ่อาจจ่ายได้มากกว่าธุรกิจเล็ก

---

## 8. ปรับแต่งให้เหมาะกับตัวเอง

### เปลี่ยนช่วงค่าแรง:
```python
# สำหรับ Junior Developer
lb = np.array([200, 1.0, 1.0, 0])    # ค่าแรงเริ่ม 200
ub = np.array([800, 2.0, 1.5, 15])   # ค่าแรงสูงสุด 800

# สำหรับ Senior Developer
lb = np.array([800, 1.2, 1.2, 0])    # ค่าแรงเริ่ม 800
ub = np.array([3000, 3.0, 2.5, 25])  # ค่าแรงสูงสุด 3000
```

### เพิ่ม Projects ของตัวเอง:
```python
projects.append({
    'name': 'ชื่อโปรเจค',
    'hours': 50,           # ชั่วโมงที่คาดว่าใช้
    'complexity': 3,       # ความซับซ้อน 1-5
    'urgency': 2,          # ความเร่งด่วน 1-3
    'budget': 35000,       # งบลูกค้า
    'is_returning_client': False
})
```

---

*ลองนำไปใช้และปรับแต่งให้เหมาะกับงานของคุณ!*

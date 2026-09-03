"""ฟังก์ชันเป้าหมาย 5 แบบจาก workshop_objective_function.pdf.

แต่ละฟังก์ชันรับเวกเตอร์หนึ่งจุด [x1, ..., xn] และคืนค่า float
รองรับ list, tuple และ NumPy array; ไม่มีการสุ่มหรือพิมพ์ผลตอน import
ฟังก์ชันคำนวณนอก search domain ได้ ผู้เรียกต้องควบคุม bounds เอง

Schwefel ใช้ 418.8929 ตาม PDF เป็นค่าเริ่มต้น หากต้องการค่ามาตรฐาน
ให้ระบุ constant=SCHWEFEL_STANDARD_CONSTANT (418.9829)
"""

from __future__ import annotations

from numbers import Integral
from typing import Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray

__all__ = [
    "paraboloid", "rosenbrock", "griewank", "schwefel", "rastrigin",
    "FUNCTIONS", "BOUNDS", "get_function", "get_bounds",
    "SCHWEFEL_PDF_CONSTANT", "SCHWEFEL_STANDARD_CONSTANT",
]

SCHWEFEL_PDF_CONSTANT = 418.8929
SCHWEFEL_STANDARD_CONSTANT = 418.9829


def _as_vector(x: ArrayLike, min_size: int = 1) -> NDArray[np.float64]:
    """ตรวจสอบว่า x เป็นเวกเตอร์จำนวนจริงที่ไม่มี NaN หรือ infinity."""
    raw = np.asarray(x)
    if np.iscomplexobj(raw):
        raise ValueError("x must contain real numbers, not complex numbers")
    values = np.asarray(raw, dtype=float)
    if values.ndim != 1 or values.size < min_size:
        raise ValueError(f"x must be a 1-D vector with at least {min_size} values")
    if not np.all(np.isfinite(values)):
        raise ValueError("x must contain only finite values (no NaN or infinity)")
    return values


def paraboloid(x: ArrayLike) -> float:
    """f(x) = sum(x_i**2); domain [-5, 5]; minimum 0 at [0, ..., 0]."""
    x = _as_vector(x)
    return float(np.sum(x**2))


def rosenbrock(x: ArrayLike) -> float:
    """f(x) = sum(100*(x[i+1]-x[i]**2)**2 + (x[i]-1)**2).

    Requires n >= 2; domain [-2.048, 2.048]; minimum 0 at [1, ..., 1].
    """
    x = _as_vector(x, min_size=2)
    return float(np.sum(100.0 * (x[1:] - x[:-1]**2)**2 + (x[:-1] - 1.0)**2))


def griewank(x: ArrayLike) -> float:
    """f(x) = 1 + sum(x_i**2)/4000 - prod(cos(x_i/sqrt(i))).

    i starts at 1; domain [-600, 600]; minimum 0 at [0, ..., 0].
    """
    x = _as_vector(x)
    indices = np.arange(1, x.size + 1, dtype=float)
    return float(1.0 + np.sum(x**2) / 4000.0 - np.prod(np.cos(x / np.sqrt(indices))))


def schwefel(x: ArrayLike, *, constant: float = SCHWEFEL_PDF_CONSTANT) -> float:
    """f(x) = constant*n - sum(x_i*sin(sqrt(abs(x_i)))); domain [-500, 500].

    ค่าเริ่มต้น 418.8929 ตรงกับ PDF แต่ทำให้ค่าที่ x_i=420.9687
    ประมาณ -0.08998727*n ไม่ใช่ 0 ตามข้อความใน PDF
    เลือก constant=SCHWEFEL_STANDARD_CONSTANT เพื่อใช้ 418.9829:
    ค่าที่จุดดังกล่าวจะประมาณ 0.00001273*n เนื่องจากการปัดเศษ
    เปลี่ยนค่าคงที่แล้วตำแหน่ง minimum ยังคงเดิม
    """
    x = _as_vector(x)
    constant = float(constant)
    if not np.isfinite(constant):
        raise ValueError("constant must be finite")
    return float(constant * x.size - np.sum(x * np.sin(np.sqrt(np.abs(x)))))


def rastrigin(x: ArrayLike) -> float:
    """f(x) = 10*n + sum(x_i**2 - 10*cos(2*pi*x_i)).

    Domain [-5.12, 5.12]; minimum 0 at [0, ..., 0].
    """
    x = _as_vector(x)
    return float(10.0 * x.size + np.sum(x**2 - 10.0 * np.cos(2.0 * np.pi * x)))


FUNCTIONS: dict[str, Callable[[ArrayLike], float]] = {
    "paraboloid": paraboloid,
    "rosenbrock": rosenbrock,
    "griewank": griewank,
    "schwefel": schwefel,
    "rastrigin": rastrigin,
}

# ขอบเขตต่อหนึ่งตัวแปร ตาม PDF
BOUNDS: dict[str, tuple[float, float]] = {
    "paraboloid": (-5.0, 5.0),
    "rosenbrock": (-2.048, 2.048),
    "griewank": (-600.0, 600.0),
    "schwefel": (-500.0, 500.0),
    "rastrigin": (-5.12, 5.12),
}


def _function_name(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    key = name.strip().lower()
    if key not in FUNCTIONS:
        raise ValueError(f"Unknown function {name!r}. Choose from: {', '.join(FUNCTIONS)}")
    return key


def get_function(name: str) -> Callable[[ArrayLike], float]:
    """เลือกฟังก์ชันจากชื่อ เช่น objective = get_function('rastrigin')."""
    return FUNCTIONS[_function_name(name)]


def get_bounds(name: str, n: int = 2) -> list[tuple[float, float]]:
    """คืน [(lower, upper), ...] จำนวน n คู่ เพื่อนำไปใช้กับ optimizer."""
    key = _function_name(name)
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, Integral):
        raise TypeError("n must be an integer")
    minimum = 2 if key == "rosenbrock" else 1
    if n < minimum:
        raise ValueError(f"{key} requires n >= {minimum}")
    return [BOUNDS[key]] * int(n)

"""Analytic inputs from the assignment and independently specified roots."""

import math
from dataclasses import dataclass
from .solvers import Function


@dataclass(frozen=True)
class Problem:
    key: str
    equation: str
    f: Function
    df: Function
    interval: tuple[float, float]
    reference: float


def repeated(x):
    return (x - 1) ** 2 * (x + 2)


def repeated_derivative(x):
    return 3 * (x - 1) * (x + 1)


PROBLEMS = (
    Problem("f1", "x³ + x − 3", lambda x: x**3 + x - 3,
            lambda x: 3*x*x + 1, (0, 4), 1.2134116627622296),
    Problem("f2", "cos(x) − x", lambda x: math.cos(x) - x,
            lambda x: -math.sin(x) - 1, (0, 1), 0.7390851332151607),
    Problem("f3", "x exp(−x) − 0.1", lambda x: x*math.exp(-x) - 0.1,
            lambda x: (1-x)*math.exp(-x), (0, 2), 0.11183255915896297),
    Problem("f4", "x³ − 2x² − 5", lambda x: x**3 - 2*x*x - 5,
            lambda x: 3*x*x - 4*x, (2, 4), 2.690647448028613),
    Problem("f5-left", "(x − 1)²(x + 2)", repeated, repeated_derivative, (-3, 0), -2.0),
    Problem("f5-right", "(x − 1)²(x + 2)", repeated, repeated_derivative, (0, 3), 1.0),
    Problem("f6", "∛x", math.cbrt,
            lambda x: math.inf if x == 0 else abs(x)**(-2/3)/3,
            (-0.001, 0.001), 0.0),
    Problem("f7", "x + sin(x) − 1", lambda x: x + math.sin(x) - 1,
            lambda x: 1 + math.cos(x), (0, 1), 0.5109734293885691),
)

# (display name, map, starting value, local derivative at the root)
FIXED_MAPS = {
    "f1": (
        ("∛(3 − x)", lambda x: math.cbrt(3-x), 1.0,
         -1/(3*PROBLEMS[0].reference**2)),
        ("3 − x³", lambda x: 3-x**3, 1.0, -3*PROBLEMS[0].reference**2),
    ),
    "f2": (
        ("cos(x)", math.cos, 0.5, -math.sin(PROBLEMS[1].reference)),
        ("arccos(x)", math.acos, 0.5, -1/math.sqrt(1-PROBLEMS[1].reference**2)),
    ),
    "f3": (
        ("0.1 exp(x)", lambda x: 0.1 * math.exp(x), 0.5, PROBLEMS[2].reference),
        ("x + f3(x)", lambda x: x + PROBLEMS[2].f(x), 0.5,
         1 + PROBLEMS[2].df(PROBLEMS[2].reference)),
    ),
    "f5-left": (
        ("x − f5(x)/10", lambda x: x - repeated(x)/10, -2.4, 0.1),
    ),
    "f5-right": (
        ("1 + 0.5(x − 1)", lambda x: (x + 1)/2, 1.5, 0.5),
    ),
}

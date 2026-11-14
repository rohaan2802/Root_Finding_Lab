"""Scalar solvers with per-iteration histories and explicit stopping reasons."""

from dataclasses import dataclass
from math import isfinite
from collections.abc import Callable

TOL_F = 1e-8
TOL_X = 1e-10
MAX_ITER = 200
TINY = 1e-14
Function = Callable[[float], float]


@dataclass(frozen=True)
class Step:
    x: float
    fx: float
    kind: str
    width: float | None = None


@dataclass(frozen=True)
class Result:
    steps: tuple[Step, ...]
    iterations: int
    status: str

    @property
    def root(self):
        return self.steps[-1].x

    @property
    def residual(self):
        return abs(self.steps[-1].fx)


def evaluate(f, x):
    """Evaluate a real scalar function, rejecting invalid iterates."""
    if not isfinite(x):
        raise ArithmeticError("non-finite iterate")
    value = f(x)
    if not isfinite(value):
        raise ArithmeticError("non-finite function value")
    return value


def limits(tol_f, tol_x, max_iter):
    if tol_f <= 0 or not isfinite(tol_f):
        raise ValueError("tol_f must be positive and finite")
    if tol_x is not None and (tol_x <= 0 or not isfinite(tol_x)):
        raise ValueError("tol_x must be positive and finite, or None")
    if type(max_iter) is not int or max_iter < 1:
        raise ValueError("max_iter must be a positive integer")


def stop(step, tol_f, tol_x, distance, label):
    if abs(step.fx) <= tol_f:
        return "residual"
    if tol_x is not None and distance <= tol_x:
        return label
    return None


def bracketed(f, a, b, tol_f, tol_x, max_iter, df=None):
    limits(tol_f, tol_x, max_iter)
    if not a < b or not isfinite(b - a):
        raise ValueError("expected ordered endpoints with finite width")
    fa, fb = evaluate(f, a), evaluate(f, b)
    for x, fx in ((a, fa), (b, fb)):
        if fx == 0:
            return Result((Step(x, fx, "endpoint", b - a),), 0, "residual")
    if (fa < 0) == (fb < 0):
        raise ValueError("endpoints must have opposite signs")

    history = []
    for iteration in range(1, max_iter + 1):
        width = b - a
        midpoint = a + width / 2
        trial = Step(midpoint, evaluate(f, midpoint), "bisection", width)
        reason = stop(trial, tol_f, tol_x, width / 2, "bracket")
        if reason:
            return Result(tuple([*history, trial]), iteration, reason)

        if df is not None:
            try:
                slope = df(midpoint)
                if isfinite(slope) and abs(slope) >= TINY:
                    candidate = midpoint - trial.fx / slope
                    # Accept only the central half, so either retained
                    # interval is at most 3/4 of the previous width.
                    if a + width / 4 <= candidate <= b - width / 4:
                        fc = evaluate(f, candidate)
                        if abs(fc) < abs(trial.fx):
                            trial = Step(candidate, fc, "newton", width)
            except (ArithmeticError, ValueError):
                pass

        history.append(trial)
        if abs(trial.fx) <= tol_f:
            return Result(tuple(history), iteration, "residual")
        if trial.x in (a, b):
            return Result(tuple(history), iteration, "stagnation")
        if (fa < 0) == (trial.fx < 0):
            a, fa = trial.x, trial.fx
        else:
            b = trial.x
    return Result(tuple(history), max_iter, "iteration-limit")


def bisection(f, a, b, *, tol_f=TOL_F, tol_x=TOL_X, max_iter=MAX_ITER):
    """Halve a sign-changing interval for a continuous function."""
    return bracketed(f, a, b, tol_f, tol_x, max_iter)


def hybrid(f, df, a, b, *, tol_f=TOL_F, tol_x=TOL_X, max_iter=MAX_ITER):
    """Try a guarded Newton step from the midpoint, with bisection fallback."""
    return bracketed(f, a, b, tol_f, tol_x, max_iter, df)


def open_iteration(f, seeds, advance, kind, tol_f, tol_x, max_iter):
    limits(tol_f, tol_x, max_iter)
    history = [Step(x, evaluate(f, x), "seed") for x in seeds]
    if abs(history[-1].fx) <= tol_f:
        return Result(tuple(history), 0, "residual")
    for iteration in range(1, max_iter + 1):
        previous = history[-1]
        try:
            x = advance(history)
            current = Step(x, evaluate(f, x), kind)
        except (ArithmeticError, ValueError) as exc:
            return Result(tuple(history), iteration - 1, str(exc))
        history.append(current)
        reason = stop(current, tol_f, tol_x, abs(x - previous.x), "step")
        if reason:
            return Result(tuple(history), iteration, reason)
        if x == previous.x:
            return Result(tuple(history), iteration, "stagnation")
    return Result(tuple(history), max_iter, "iteration-limit")


def fixed_point(f, g, x0, *, tol_f=TOL_F, tol_x=TOL_X, max_iter=MAX_ITER):
    """Iterate x = g(x) and track the residual of the original equation."""
    return open_iteration(
        f, (x0,), lambda history: g(history[-1].x),
        "fixed-point", tol_f, tol_x, max_iter,
    )


def newton(f, df, x0, *, tol_f=TOL_F, tol_x=TOL_X, max_iter=MAX_ITER):
    """Apply Newton updates with a finite, nonzero slope check."""
    def advance(history):
        step = history[-1]
        slope = df(step.x)
        if not isfinite(slope) or abs(slope) < TINY:
            raise ArithmeticError("unusable derivative")
        return step.x - step.fx / slope

    return open_iteration(f, (x0,), advance, "newton", tol_f, tol_x, max_iter)


def secant(f, x0, x1, *, tol_f=TOL_F, tol_x=TOL_X, max_iter=MAX_ITER):
    """Approximate the slope using the two most recent points."""
    def advance(history):
        left, right = history[-2:]
        change = right.fx - left.fx
        if not isfinite(change) or abs(change) < TINY:
            raise ArithmeticError("unusable secant slope")
        return right.x - right.fx * ((right.x - left.x) / change)

    limits(tol_f, tol_x, max_iter)
    first = Step(x0, evaluate(f, x0), "seed")
    if abs(first.fx) <= tol_f:
        return Result((first,), 0, "residual")
    return open_iteration(f, (x0, x1), advance, "secant", tol_f, tol_x, max_iter)

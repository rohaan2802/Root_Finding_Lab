"""Run the assignment experiments and export reviewable CSV files."""

import argparse
import csv
import math
from pathlib import Path
from statistics import median
from timeit import Timer

from .problems import FIXED_MAPS, PROBLEMS
from .solvers import bisection, fixed_point, hybrid, newton, secant

METHODS = ("Bisection", "Fixed-point", "Newton", "Secant", "Hybrid")
TARGET = 1e-10


def bracketing_rows():
    for p in PROBLEMS:
        a, b = p.interval
        fa, fb = p.f(a), p.f(b)
        yield dict(case=p.key, equation=p.equation, a=a, b=b,
                   fa=fa, fb=fb, sign_change=(fa < 0 < fb or fb < 0 < fa),
                   reference=p.reference)


def tasks(p, **options):
    a, b = p.interval
    middle = a + (b-a)/2
    calls = {
        "Bisection": lambda: bisection(p.f, a, b, **options),
        "Newton": lambda: newton(p.f, p.df, middle, **options),
        "Secant": lambda: secant(p.f, a, b, **options),
        "Hybrid": lambda: hybrid(p.f, p.df, a, b, **options),
    }
    if p.key in FIXED_MAPS:
        _, g, seed, _ = FIXED_MAPS[p.key][0]
        calls["Fixed-point"] = lambda: fixed_point(p.f, g, seed, **options)
    return {method: calls[method] for method in METHODS if method in calls}


def result_row(p, method, seed, run):
    try:
        result = run()
    except ValueError as exc:
        return dict(case=p.key, method=method, seed=seed, root=None, iterations=None,
                    residual=None, x_error=None, in_interval=None, status=str(exc))
    return dict(case=p.key, method=method, seed=seed, root=result.root,
                iterations=result.iterations, residual=result.residual,
                x_error=abs(result.root-p.reference),
                in_interval=p.interval[0] <= result.root <= p.interval[1],
                status=result.status)


def experiment_rows():
    for p in PROBLEMS:
        a, b = p.interval
        width = b-a
        points = tuple(a + width*fraction for fraction in (.25, .5, .75))
        for method in ("Bisection", "Hybrid"):
            yield result_row(p, method, str(p.interval), tasks(p)[method])
        for x in points:
            yield result_row(p, "Newton", str(x), lambda: newton(p.f, p.df, x))
        for x, y in ((a, b), points[:2], points[1:]):
            yield result_row(p, "Secant", str((x, y)), lambda: secant(p.f, x, y))
        for label, g, seed, slope in FIXED_MAPS.get(p.key, ()):
            yield result_row(
                p, "Fixed-point", f"{label} at {seed}; |g′|={abs(slope):.3f}",
                lambda: fixed_point(p.f, g, seed),
            )


def traces(p):
    for method, run in tasks(p, tol_f=1e-15, tol_x=None).items():
        try:
            yield method, run()
        except ValueError:
            continue


def observed_order(errors):
    """Return the latest usable three-point estimate before the rounding floor."""
    for a, b, c in reversed(list(zip(errors, errors[1:], errors[2:]))):
        if a > b > c > 1e-14:
            denominator = math.log(b/a)
            if abs(denominator) > 0.05:
                return math.log(c/b) / denominator
    return None


def convergence_rows():
    for p in (PROBLEMS[0], PROBLEMS[1], PROBLEMS[4], PROBLEMS[5]):
        for method, result in traces(p):
            errors = [abs(step.x-p.reference) for step in result.steps]
            yield dict(case=p.key, method=method, samples=len(errors),
                       order=observed_order(errors), status=result.status)


def benchmark_rows():
    """Time only solver calls, using seven batches of 200 per successful run."""
    for p in PROBLEMS[:3]:
        for method, run in tasks(p, tol_f=TARGET, tol_x=None).items():
            result = run()
            matched = result.residual <= TARGET
            samples = Timer(run).repeat(repeat=7, number=200) if matched else []
            yield dict(case=p.key, method=method, root=result.root,
                       iterations=result.iterations, residual=result.residual,
                       target_met=matched, status=result.status,
                       median_us=median(samples)*1e6/200 if matched else None)


def write_csv(path, records):
    rows = list(records)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results"))
    output = parser.parse_args().output
    output.mkdir(parents=True, exist_ok=True)
    for name, records in (
        ("bracketing", bracketing_rows()),
        ("solver_runs", experiment_rows()),
        ("convergence_order", convergence_rows()),
        ("benchmark", benchmark_rows()),
    ):
        write_csv(output / f"{name}.csv", records)
    print(f"Wrote four experiment tables to {output}")


if __name__ == "__main__":
    main()

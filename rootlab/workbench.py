"""Run and inspect a single case from the command line or desktop app."""

import argparse
import csv
import math
from pathlib import Path

from .experiments import METHODS, tasks
from .problems import FIXED_MAPS, PROBLEMS
from .solvers import MAX_ITER, TOL_F, TOL_X, fixed_point, hybrid, newton, secant, bisection

CASES = {problem.key: problem for problem in PROBLEMS}


def solve_case(case, method, *, seeds=None, tol_f=TOL_F, tol_x=TOL_X, max_iter=MAX_ITER):
    """Run a named solver with case defaults or user-supplied starting points."""
    if method not in METHODS:
        raise ValueError(f"Unknown solver: {method}")
    problem = CASES[case]
    options = dict(tol_f=tol_f, tol_x=tol_x, max_iter=max_iter)
    if seeds is None:
        if method not in tasks(problem, **options):
            raise ValueError(f"No fixed-point map is included for {case}.")
        return tasks(problem, **options)[method]()
    expected = 1 if method in ("Newton", "Fixed-point") else 2
    if len(seeds) != expected or not all(map(math.isfinite, seeds)):
        raise ValueError(f"{method} requires {expected} finite starting points.")
    f, df = problem.f, problem.df
    if method == "Bisection":
        return bisection(f, *seeds, **options)
    if method == "Hybrid":
        return hybrid(f, df, *seeds, **options)
    if method == "Newton":
        return newton(f, df, *seeds, **options)
    if method == "Secant":
        return secant(f, *seeds, **options)
    if case not in FIXED_MAPS:
        raise ValueError(f"No fixed-point map is included for {case}.")
    return fixed_point(f, FIXED_MAPS[case][0][1], *seeds, **options)


def trace_rows(problem, result):
    """Yield the indexed history with both residual and reference error."""
    for index, step in enumerate(result.steps):
        yield (index, step.kind, step.x, step.fx, abs(step.fx),
               abs(step.x - problem.reference), step.width)


TRACE_COLUMNS = ("point", "step", "x", "fx", "residual", "reference_error", "bracket_width")


def export_trace(path, problem, result):
    with Path(path).open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(TRACE_COLUMNS)
        writer.writerows(trace_rows(problem, result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, default="f3")
    parser.add_argument("--method", choices=METHODS, default="Hybrid")
    parser.add_argument("--seeds", type=float, nargs="+")
    parser.add_argument("--tol-f", type=float, default=TOL_F)
    parser.add_argument("--tol-x", type=float, default=TOL_X)
    parser.add_argument("--max-iter", type=int, default=MAX_ITER)
    parser.add_argument("--strict", action="store_true", help="Stop on residual or breakdown only.")
    parser.add_argument("--trace", type=Path, help="Export the recorded points as CSV.")
    args = parser.parse_args()
    try:
        result = solve_case(args.case, args.method, seeds=args.seeds,
                            tol_f=args.tol_f, tol_x=None if args.strict else args.tol_x,
                            max_iter=args.max_iter)
        problem = CASES[args.case]
        if args.trace:
            export_trace(args.trace, problem, result)
    except (ArithmeticError, ValueError, OSError) as error:
        parser.exit(2, f"{error}\n")
    inside = problem.interval[0] <= result.root <= problem.interval[1]
    print(f"{args.case} | {args.method} | {result.status}")
    print(f"x = {result.root:.15g} | residual = {result.residual:.3e} | updates = {result.iterations}")
    print(f"Reference error = {abs(result.root-problem.reference):.3e} | assigned interval: {'inside' if inside else 'outside'}")


if __name__ == "__main__":
    main()

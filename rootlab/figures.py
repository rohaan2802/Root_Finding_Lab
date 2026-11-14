"""Render the 24 gallery figures from live traces, source, and saved CSVs."""

import argparse
import csv
import inspect
import json
import math
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

from . import solvers
from .experiments import traces
from .problems import PROBLEMS

ROOT = Path(__file__).resolve().parents[1]
INK = "#161b38"
MUTED = "#495575"
PAPER = "#f5f3ff"
COLORS = ("#126b70", "#51409c", "#a43c19", "#8d3b78", "#756000")
CATALOG = []


def canvas(title):
    fig = plt.figure(figsize=(12, 7.5), dpi=120, facecolor=PAPER)
    fig.text(.075, .91, title, color=INK, fontsize=27, weight="bold")
    return fig


def chart(title, xlabel, ylabel):
    fig = canvas(title)
    ax = fig.add_axes((.13, .14, .80, .67), facecolor="#ffffff")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=.22)
    ax.set_axisbelow(True)
    ax.set(xlabel=xlabel, ylabel=ylabel)
    return fig, ax


def export(fig, title, category, caption):
    name = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    full = f"assets/screenshots/{name}.png"
    preview = f"assets/thumbs/{name}.webp"
    fig.savefig(ROOT / full, dpi=120)
    plt.close(fig)
    with Image.open(ROOT / full) as image:
        image.convert("RGB").resize((960, 600), Image.Resampling.LANCZOS).save(
            ROOT / preview, quality=88, method=6,
        )
    CATALOG.append(dict(title=title, category=category, caption=caption,
                        full=full, preview=preview))


def inputs():
    captions = (
        "The cubic is strictly increasing and crosses zero once on [0, 4].",
        "The intersection of cos(x) and x appears as a zero on [0, 1].",
        "The bracket isolates the smaller root. Its midpoint x = 1 has zero slope.",
        "The cubic changes sign on [2, 4], which excludes its stationary points.",
        "The simple root at −2 crosses the axis within [−3, 0].",
        "The double root at 1 touches the axis. Both endpoints are positive.",
        "The real cube root crosses zero with a vertical tangent.",
        "The chosen continuous test function crosses zero between 0 and 1.",
    )
    for p, caption in zip(PROBLEMS, captions, strict=True):
        title = f"{p.key.upper()} function profile"
        fig, ax = chart(title, "x", "f(x)")
        a, b = p.interval
        xs = [a + (b-a)*k/400 for k in range(401)]
        ax.plot(xs, [p.f(x) for x in xs], color=COLORS[0], linewidth=2.6,
                label=p.equation)
        ax.axhline(0, color=MUTED, linewidth=1)
        ax.scatter([a, b], [p.f(a), p.f(b)], color=COLORS[1], label="Endpoints")
        ax.scatter(p.reference, 0, color=COLORS[2], s=65, zorder=4,
                   label=f"Root ≈ {p.reference:.6g}")
        ax.legend(loc="best")
        export(fig, title, "Inputs", caption)


def convergence():
    for p in (PROBLEMS[0], PROBLEMS[1], PROBLEMS[4], PROBLEMS[5]):
        runs = list(traces(p))
        for residual in (True, False):
            metric = "residual" if residual else "root error"
            title = f"{p.key.upper()} {metric} traces"
            fig, ax = chart(title, "Recorded point index",
                            "|f(x)|" if residual else "|x − reference|")
            for (method, result), color in zip(runs, COLORS, strict=False):
                values = [abs(s.fx) if residual else abs(s.x-p.reference)
                          for s in result.steps]
                ax.semilogy([max(value, 1e-17) for value in values],
                            ".-", color=color, linewidth=2.2, label=method)
            ax.legend(loc="best")
            detail = ("Bisection and hybrid reject the same-sign interval."
                      if p.key == "f5-right" else "Each curve uses the same analytic case.")
            caption = (f"Recorded {metric}; values below 10⁻¹⁷ are plotted at the floor. "
                       + detail)
            export(fig, title, "Convergence", caption)


def read_rows(name, directory):
    with (directory / f"{name}.csv").open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def table(title, headers, rows, caption):
    fig = canvas(title)
    ax = fig.add_axes((.075, .12, .85, .70))
    ax.axis("off")
    tbl = ax.table(cellText=rows, colLabels=headers, cellLoc="center",
                   bbox=(0, 0, 1, 1))
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(14 if len(rows) < 10 else 12)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor("#c3d5d2")
        cell.set_facecolor("#31265d" if row == 0 else ["#eae6fa", "#ffffff"][row % 2])
        cell.get_text().set_color("#ffffff" if row == 0 else INK)
        if row == 0:
            cell.get_text().set_weight("bold")
    export(fig, title, "Results", caption)


def report(directory):
    bracket = read_rows("bracketing", directory)
    table("Endpoint sign checks", ["Case", "f(a)", "f(b)", "Sign change"],
          [[r["case"], f'{float(r["fa"]):.4g}', f'{float(r["fb"]):.4g}',
            "Yes" if r["sign_change"] == "True" else "No"] for r in bracket],
          "Seven intervals change sign. The double-root interval is the exception.")
    runs = read_rows("solver_runs", directory)
    fixed = [r for r in runs if r["method"] == "Fixed-point" and len(r["case"]) == 2]
    table("Fixed-point map comparison", ["Case", "Map g(x)", "|g′| at root", "Updates", "Outcome"],
          [[r["case"], r["seed"].split(" at ")[0], r["seed"].split("=")[-1], r["iterations"],
            r["status"] if r["status"] in ("residual", "iteration-limit") else "Breakdown"]
           for r in fixed],
          "Two maps per equation show contraction, overflow, a domain exit, and an iteration cap.")
    orders = read_rows("convergence_order", directory)
    selected = [r for r in orders if r["method"] in ("Newton", "Secant")]
    table("Observed convergence order", ["Case", "Method", "Samples", "Local estimate"],
          [[r["case"], r["method"], r["samples"],
            f'{float(r["order"]):.3f}' if r["order"] else "—"] for r in selected],
          "Newton is near order two at simple roots and near one at the double root.")
    timing = read_rows("benchmark", directory)
    title = "Time to residual threshold"
    fig, ax = chart(title, "Analytic case", "Median microseconds per solve")
    methods = list(dict.fromkeys(r["method"] for r in timing))
    for i, (method, color) in enumerate(zip(methods, COLORS, strict=True)):
        first = True
        for j, case in enumerate(("f1", "f2", "f3")):
            row = next(r for r in timing if r["method"] == method and r["case"] == case)
            position = j + (i-2)*.15
            if row["median_us"]:
                ax.bar(position, float(row["median_us"]), .14, color=color,
                       label=method if first else None)
                first = False
            else:
                ax.scatter(position, 0, marker="x", color=color, zorder=5)
    ax.set_xticks([0, 1, 2], ["f1", "f2", "f3"])
    ax.legend(ncols=3, loc="upper left", fontsize=13)
    ax.set_ylim(top=ax.get_ylim()[1]*1.3)
    export(fig, title, "Results",
           "Seven batches of 200 solves per bar. The × marks Newton’s flat-derivative failure on f3.")
    p = PROBLEMS[2]
    result = solvers.hybrid(p.f, p.df, *p.interval, tol_f=1e-10, tol_x=None)
    indexed = list(enumerate(result.steps, 1))
    table("Hybrid fallback and recovery", ["Update", "Accepted step", "x", "|f(x)|"],
          [[i, s.kind, f"{s.x:.10f}", f"{abs(s.fx):.3e}"]
           for i, s in indexed[:4] + indexed[-3:]],
          "Selected rows from the f3 trace show the first bisection step and the final residual.")
    selected = [r for r in runs if r["case"] == "f5-right" and r["method"] == "Newton"]
    table("Residual versus position error", ["Newton seed", "|f(x)|", "|x − 1|"],
          [[r["seed"], f'{float(r["residual"]):.3e}', f'{float(r["x_error"]):.3e}']
           for r in selected],
          "At the double root, residuals below 10⁻⁸ coexist with position errors above 10⁻⁵.")


def code():
    for title, source, caption in (
        ("Newton derivative guard", inspect.getsource(solvers.newton),
         "The solver checks slope finiteness and magnitude before dividing."),
        ("Secant slope guard", inspect.getsource(solvers.secant),
         "The secant update uses two function values and detects a vanishing denominator."),
    ):
        lines = source.strip().splitlines()
        fig = canvas(title)
        ax = fig.add_axes((.07, .12, .86, .70), facecolor="#ece9fa")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("#c3d5d2")
        for i, line in enumerate(lines):
            ax.text(.033, .905-i*.85/len(lines), line, family="monospace",
                    fontsize=15, color=INK, va="top")
        export(fig, title, "Source", caption)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    plt.rcParams.update({"font.size": 16, "text.color": INK, "axes.labelcolor": INK})
    inputs()
    convergence()
    report(args.results)
    code()
    (ROOT / "assets/figures.json").write_text(
        json.dumps(CATALOG, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(f"Rendered {len(CATALOG)} figures and previews")


if __name__ == "__main__":
    main()

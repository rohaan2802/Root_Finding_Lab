<div align="center">

# Root Finding Lab

**Five scalar solvers, seven analytic equations, and a reproducible study of convergence and failure.**

[![Python 3.14](https://img.shields.io/badge/Python-3.14-245e70?style=for-the-badge&logo=python&logoColor=white)](rootlab/solvers.py)
[![Experiment notebook](https://img.shields.io/badge/Jupyter-experiment_notebook-995022?style=for-the-badge&logo=jupyter&logoColor=white)](notebooks/root_finding_study.ipynb)
[![Saved results](https://img.shields.io/badge/Results-saved_CSVs-14665a?style=for-the-badge)](results/benchmark.csv)

[![Desktop workbench](https://img.shields.io/badge/Desktop-Tkinter-5442A6?style=for-the-badge&logo=python&logoColor=white)](rootlab/desktop.py)
[![Trace charts](https://img.shields.io/badge/Charts-Matplotlib-205E78?style=for-the-badge&logo=plotly&logoColor=white)](#figure-index)
[![Command line](https://img.shields.io/badge/CLI-Custom_runs-384767?style=for-the-badge&logo=gnubash&logoColor=white)](#command-line)
[![Test suite](https://img.shields.io/badge/Tests-unittest-286B59?style=for-the-badge&logo=checkmarx&logoColor=white)](tests/)

</div>

## Live Links

| What | Link |
| --- | --- |
| Repository | [https://github.com/rohaan2802/Root_Finding_Lab](https://github.com/rohaan2802/Root_Finding_Lab) |
| GitHub Pages | [https://rohaan2802.github.io/Root_Finding_Lab/](https://rohaan2802.github.io/Root_Finding_Lab/) |
| Experiment notebook | [https://github.com/rohaan2802/Root_Finding_Lab/blob/main/notebooks/root_finding_study.ipynb](https://github.com/rohaan2802/Root_Finding_Lab/blob/main/notebooks/root_finding_study.ipynb) |

## Table of Contents

[Live Links](#live-links) · [Overview](#overview) · [What's Inside](#whats-inside) · [Project Breakdown](#project-breakdown) · [Interactive Workbench](#interactive-workbench) · [Experiment Design](#experiment-design) · [Folder Structure](#folder-structure) · [Setup](#setup) · [Results](#results) · [Limitations](#limitations) · [Figure Index](#figure-index) · [About the Author](#about-the-author)

## Overview

Root Finding Lab compares five numerical methods for solving f(x) = 0. The Fall 2025 CS2008 Numerical Computing study uses seven analytic equations across eight intervals, including a double root, a flat initial derivative, and a cube root with a vertical tangent.

The inputs are the equations, their derivatives, prescribed intervals, and starting points in [problems.py](rootlab/problems.py). They require no external dataset.

## What's Inside

| Material | Contents |
| --- | --- |
| [Study notebook](notebooks/root_finding_study.ipynb) | Executed Q1–Q8 analysis, plots, and live experiment cells |
| [Desktop workbench](rootlab/desktop.py) and [CLI](rootlab/workbench.py) | Live solver runs, adjustable starts and tolerances, charts and CSV export |
| [Python source](rootlab/solvers.py) | Reusable solvers and per-iterate histories |
| [Experiments](rootlab/experiments.py) | Endpoint checks, seed sweeps, local order estimates, and repeated timings |
| [Saved results](results/) | Four CSV tables for local inspection |
| [Assignment brief](docs/assignment_brief.pdf) and [method notes](docs/method_notes.md) | Original requirements and details of the numerical choices |
| [Original submission](archive/) | Preserved notebook and audit notes |
| [Project webpage](index.html) | Responsive reader and 24-figure gallery |

## Project Breakdown

| Method | What it uses | What the experiments check |
| --- | --- | --- |
| Bisection | Opposite signs at interval endpoints | Ordered bracket, endpoint roots, and interval contraction |
| Fixed-point iteration | A chosen map g(x) | Two maps each for f1–f3, with local slopes and failure outcomes |
| Newton–Raphson | One seed and an analytic derivative | Three initial guesses per interval, including the f3 flat midpoint |
| Secant | Two seeds and function evaluations | Three pairs per interval, a near-zero denominator guard, and roots outside the interval |
| Safeguarded Newton | A valid bracket and an analytic derivative | Accepts a central Newton proposal if it lowers the residual, otherwise bisects |

Default stopping thresholds are 10⁻⁸ for the residual and 10⁻¹⁰ for the absolute step or midpoint error bound, with at most 200 updates. The solver reports the actual exit condition. The strict benchmark disables step and bracket stops and measures the median of seven batches of 200 solves.

## Interactive Workbench

Double-click [launch_workbench.cmd](launch_workbench.cmd) on Windows after installing the dependencies, or run `python -m rootlab.desktop` from an activated environment. The [desktop app](rootlab/desktop.py) opens on f3 with the hybrid solver selected. It shows the equation, assigned interval, result, exit reason, two live charts, and a scrollable trace.

1. Select one of eight intervals and choose a solver. Blank seeds use the experiment defaults.
2. For Newton or Fixed-point, enter one starting value. For Secant, enter two initial points. For Bisection or Hybrid, enter two ordered bracket endpoints.
3. Set the residual tolerance and step tolerance, or enable residual-only stopping. Run the solver and inspect the residual, reference error, and interval membership.
4. Export the trace as CSV. The rows include the recorded point, step type, estimate, signed function value, absolute residual, reference error, and bracket width where applicable.

The [web comparison](index.html#try-it) displays Python-generated traces for f2, f3, and f5-right. Try f3 with Newton, Secant, and Hybrid to see three distinct outcomes on the same equation. Use the desktop app or CLI to change seeds and tolerances and compute a fresh run.

### Command Line

```powershell
.venv\Scripts\python.exe -m rootlab.workbench --case f3 --method Newton --seeds 0.2 --strict --tol-f 1e-10
.venv\Scripts\python.exe -m rootlab.workbench --case f3 --method Hybrid --strict --tol-f 1e-10 --trace f3_trace.csv
```

The first command changes Newton’s starting point from the flat midpoint to 0.2. The second exports the safeguard’s iteration history. Use `--help` to see all cases, solvers, and tolerance options. Export files are created only when a destination is supplied.

## Experiment Design

| Case | Equation | Interval | Reference root | What it isolates |
| --- | --- | --- | --- | --- |
| f1 | x³ + x − 3 | [0, 4] | 1.2134116628 | Smooth increasing cubic |
| f2 | cos(x) − x | [0, 1] | 0.7390851332 | Contraction and open-method comparison |
| f3 | x exp(−x) − 0.1 | [0, 2] | 0.1118325592 | Flat midpoint and an external root |
| f4 | x³ − 2x² − 5 | [2, 4] | 2.6906474480 | Polynomial seed sensitivity |
| f5-left | (x − 1)²(x + 2) | [−3, 0] | −2 | Simple sign-changing root |
| f5-right | (x − 1)²(x + 2) | [0, 3] | 1 | Same-sign endpoints and slow convergence |
| f6 | ∛x | [−0.001, 0.001] | 0 | Infinite derivative at the root |
| f7 | x + sin(x) − 1 | [0, 1] | 0.5109734294 | An additional smooth continuous equation |

The solver layer records each accepted point once. The experiment layer reads that history for tables, timing, and convergence plots. The notebook, GUI, and CLI call the same solver code. The website reads generated examples from [demo-data.js](assets/js/demo-data.js), which can be refreshed with `python -m rootlab.demo`.

## Folder Structure

```text
Root_Finding_Lab/
├── launch_workbench.cmd               Windows desktop launcher
├── index.html                         GitHub Pages entry point
├── assets/                            Site CSS, JS, figures and previews
├── archive/                           Original assignment notebook
├── docs/                              Assignment brief and numerical notes
├── notebooks/root_finding_study.ipynb  Executed Q1–Q8 notebook
├── results/                           Four saved CSV tables
├── rootlab/                           Solvers, inputs, experiments, figures
├── tests/                             Numerical and workbench regression checks
└── requirements.txt                   Notebook and figure dependencies
```

## Setup

Use Python 3.14 from the repository root. In PowerShell run:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m rootlab.experiments --output build/results
.venv\Scripts\python.exe -m http.server 8000
```

Open the [local site](http://localhost:8000/) while the server is running. Opening [index.html](index.html) directly also supports the gallery. To recompute notebook cells, open the study notebook in a Jupyter-compatible editor, select the environment created above, and run all cells. From the repository root, `python -m rootlab.figures --results build/results` refreshes the gallery images from regenerated results when run in the same environment.

## Results

In the saved strict-residual benchmark, 14 of 15 runs reached |f(x)| ≤ 10⁻¹⁰. The f3 Newton trial stopped at x = 1 with an unusable derivative. Secant met the threshold at x ≈ 3.577152, outside [0, 2]. The hybrid recovered via bisection and reached the intended root near 0.1118325592.

| Saved output | What to inspect |
| --- | --- |
| [Endpoint signs](results/bracketing.csv) | Seven sign changes and the same-sign f5-right interval |
| [Solver runs](results/solver_runs.csv) | Root estimates, residuals, absolute position errors, interval membership, and exit status |
| [Convergence order](results/convergence_order.csv) | Local estimates near two for Newton on simple roots and near one on f5-right |
| [Timing results](results/benchmark.csv) | Residual-target status and median microseconds per successful call |

The CSV files, gallery, and notebook outputs are saved snapshots. The test and experiment commands compute fresh results locally. The notebook outputs come from a separate run, so timing can differ from the saved CSV.

## Limitations

Bracketing assumes continuity and an endpoint sign change or exact endpoint root. Open methods can leave the assigned interval, and local fixed-point slopes depend on the map and seed. Near the f5 double root, a small residual can coexist with substantial error in x. Timing varies by machine and includes trace recording. Convergence order estimates depend on the selected samples, and bisection point errors can oscillate even though its bracket halves. The f5-right fixed-point map uses the known factor at x = 1 as a teaching example.

## Figure Index

Select a preview to open the 1440 × 900 figure.

### F1 function profile

<a href="assets/screenshots/f1_function_profile.png"><img src="assets/thumbs/f1_function_profile.webp" width="720" height="450" alt="F1 function profile"></a>

The cubic is strictly increasing and crosses zero once on [0, 4].

### F2 function profile

<a href="assets/screenshots/f2_function_profile.png"><img src="assets/thumbs/f2_function_profile.webp" width="720" height="450" alt="F2 function profile"></a>

The intersection of cos(x) and x appears as a zero on [0, 1].

### F3 function profile

<a href="assets/screenshots/f3_function_profile.png"><img src="assets/thumbs/f3_function_profile.webp" width="720" height="450" alt="F3 function profile"></a>

The bracket isolates the smaller root. Its midpoint x = 1 has zero slope.

### F4 function profile

<a href="assets/screenshots/f4_function_profile.png"><img src="assets/thumbs/f4_function_profile.webp" width="720" height="450" alt="F4 function profile"></a>

The cubic changes sign on [2, 4], which excludes its stationary points.

### F5-LEFT function profile

<a href="assets/screenshots/f5_left_function_profile.png"><img src="assets/thumbs/f5_left_function_profile.webp" width="720" height="450" alt="F5-LEFT function profile"></a>

The simple root at −2 crosses the axis within [−3, 0].

### F5-RIGHT function profile

<a href="assets/screenshots/f5_right_function_profile.png"><img src="assets/thumbs/f5_right_function_profile.webp" width="720" height="450" alt="F5-RIGHT function profile"></a>

The double root at 1 touches the axis. Both endpoints are positive.

### F6 function profile

<a href="assets/screenshots/f6_function_profile.png"><img src="assets/thumbs/f6_function_profile.webp" width="720" height="450" alt="F6 function profile"></a>

The real cube root crosses zero with a vertical tangent.

### F7 function profile

<a href="assets/screenshots/f7_function_profile.png"><img src="assets/thumbs/f7_function_profile.webp" width="720" height="450" alt="F7 function profile"></a>

The chosen continuous test function crosses zero between 0 and 1.

### F1 residual traces

<a href="assets/screenshots/f1_residual_traces.png"><img src="assets/thumbs/f1_residual_traces.webp" width="720" height="450" alt="F1 residual traces"></a>

Recorded residual; values below 10⁻¹⁷ are plotted at the floor. Each curve uses the same analytic case.

### F1 root error traces

<a href="assets/screenshots/f1_root_error_traces.png"><img src="assets/thumbs/f1_root_error_traces.webp" width="720" height="450" alt="F1 root error traces"></a>

Recorded root error; values below 10⁻¹⁷ are plotted at the floor. Each curve uses the same analytic case.

### F2 residual traces

<a href="assets/screenshots/f2_residual_traces.png"><img src="assets/thumbs/f2_residual_traces.webp" width="720" height="450" alt="F2 residual traces"></a>

Recorded residual; values below 10⁻¹⁷ are plotted at the floor. Each curve uses the same analytic case.

### F2 root error traces

<a href="assets/screenshots/f2_root_error_traces.png"><img src="assets/thumbs/f2_root_error_traces.webp" width="720" height="450" alt="F2 root error traces"></a>

Recorded root error; values below 10⁻¹⁷ are plotted at the floor. Each curve uses the same analytic case.

### F5-LEFT residual traces

<a href="assets/screenshots/f5_left_residual_traces.png"><img src="assets/thumbs/f5_left_residual_traces.webp" width="720" height="450" alt="F5-LEFT residual traces"></a>

Recorded residual; values below 10⁻¹⁷ are plotted at the floor. Each curve uses the same analytic case.

### F5-LEFT root error traces

<a href="assets/screenshots/f5_left_root_error_traces.png"><img src="assets/thumbs/f5_left_root_error_traces.webp" width="720" height="450" alt="F5-LEFT root error traces"></a>

Recorded root error; values below 10⁻¹⁷ are plotted at the floor. Each curve uses the same analytic case.

### F5-RIGHT residual traces

<a href="assets/screenshots/f5_right_residual_traces.png"><img src="assets/thumbs/f5_right_residual_traces.webp" width="720" height="450" alt="F5-RIGHT residual traces"></a>

Recorded residual; values below 10⁻¹⁷ are plotted at the floor. Bisection and hybrid reject the same-sign interval.

### F5-RIGHT root error traces

<a href="assets/screenshots/f5_right_root_error_traces.png"><img src="assets/thumbs/f5_right_root_error_traces.webp" width="720" height="450" alt="F5-RIGHT root error traces"></a>

Recorded root error; values below 10⁻¹⁷ are plotted at the floor. Bisection and hybrid reject the same-sign interval.

### Endpoint sign checks

<a href="assets/screenshots/endpoint_sign_checks.png"><img src="assets/thumbs/endpoint_sign_checks.webp" width="720" height="450" alt="Endpoint sign checks"></a>

Seven intervals change sign. The double-root interval is the exception.

### Fixed-point map comparison

<a href="assets/screenshots/fixed_point_map_comparison.png"><img src="assets/thumbs/fixed_point_map_comparison.webp" width="720" height="450" alt="Fixed-point map comparison"></a>

Two maps per equation show contraction, overflow, a domain exit, and an iteration cap.

### Observed convergence order

<a href="assets/screenshots/observed_convergence_order.png"><img src="assets/thumbs/observed_convergence_order.webp" width="720" height="450" alt="Observed convergence order"></a>

Newton is near order two at simple roots and near one at the double root.

### Time to residual threshold

<a href="assets/screenshots/time_to_residual_threshold.png"><img src="assets/thumbs/time_to_residual_threshold.webp" width="720" height="450" alt="Time to residual threshold"></a>

Seven batches of 200 solves per bar. The × marks Newton’s flat-derivative failure on f3.

### Hybrid fallback and recovery

<a href="assets/screenshots/hybrid_fallback_and_recovery.png"><img src="assets/thumbs/hybrid_fallback_and_recovery.webp" width="720" height="450" alt="Hybrid fallback and recovery"></a>

Selected rows from the f3 trace show the first bisection step and the final residual.

### Residual versus position error

<a href="assets/screenshots/residual_versus_position_error.png"><img src="assets/thumbs/residual_versus_position_error.webp" width="720" height="450" alt="Residual versus position error"></a>

At the double root, residuals below 10⁻⁸ coexist with position errors above 10⁻⁵.

### Newton derivative guard

<a href="assets/screenshots/newton_derivative_guard.png"><img src="assets/thumbs/newton_derivative_guard.webp" width="720" height="450" alt="Newton derivative guard"></a>

The solver checks slope finiteness and magnitude before dividing.

### Secant slope guard

<a href="assets/screenshots/secant_slope_guard.png"><img src="assets/thumbs/secant_slope_guard.webp" width="720" height="450" alt="Secant slope guard"></a>

The secant update uses two function values and detects a vanishing denominator.

## About the Author

**Mohammad Rohaan** developed the original study for CS2008 Numerical Computing at FAST-NUCES in Fall 2025. The project demonstrates numerical implementation, experiment design, and analysis of solver failure cases. [GitHub profile](https://github.com/rohaan2802)


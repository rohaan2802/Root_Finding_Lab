# Numerical method notes

The default tolerances are an absolute residual of 10⁻⁸ and an absolute step or midpoint error bound of 10⁻¹⁰ with up to 200 updates. Reported stop reasons distinguish the residual, step, bracket, iteration cap, stagnation, and arithmetic failures. Reference error is measured against the expected root of the assigned interval.

## Safeguarded Newton

Each cycle evaluates the midpoint. A Newton proposal is accepted if its derivative is usable, it lands within the central half of the bracket, and it reduces the absolute residual compared with the midpoint. Otherwise the midpoint is accepted. Either accepted point updates the sign-changing interval. The central-half restriction contracts the bracket by at least 25% per nonterminal update in exact arithmetic. A midpoint width stop applies to the midpoint itself. This midpoint-based safeguard can spend more updates than Newton or ordinary bisection.

## Fixed-point maps

For f1, compare ∛(3−x) with 3−x³. For f2, compare cos(x) with arccos(x). For f3, compare 0.1 exp(x) with x+f3(x). The first map in each pair has local slope magnitude below one at the assigned root. The competing maps show overflow, a domain exit, or attraction toward another root. The slope test is local. For f5-left use x−f5(x)/10. The f5-right map uses the known factor x−1, so it is an illustrative linear iteration around the already identified root.

## Convergence and timing

The convergence figures count recorded points, including initial seeds for open methods. Plots floor very small values at 10⁻¹⁷. The order estimate uses the last strictly decreasing, adequately separated triple above 10⁻¹⁴ and is sensitive to transient behavior and floating-point rounding. Newton is approximately quadratic on the simple roots studied and approximately linear at the double root. Secant approaches superlinear behavior on f1 and f2. Bisection's interval width halves each time, while its pointwise error can be irregular. Hybrid estimates mix step types.

Timing uses the best of the tested fixed-point maps for each of f1–f3. The median of seven batches of 200 calls includes trace recording. Step and bracket stopping are disabled for the strict residual target. A failed target has no reported duration. The f3 Secant result satisfies the residual target at a different root (about 3.577152), which is outside the assigned interval. Timing depends on the machine and runtime. The CSV exposes root and status so that timing can be interpreted together with correctness.

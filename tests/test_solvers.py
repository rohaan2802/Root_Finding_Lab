import math
import unittest

from rootlab.experiments import TARGET, benchmark_rows, bracketing_rows
from rootlab.problems import PROBLEMS
from rootlab.solvers import bisection, fixed_point, hybrid, newton, secant


class SolverTests(unittest.TestCase):
    def test_reference_roots(self):
        for p in PROBLEMS:
            with self.subTest(p=p.key):
                self.assertLess(abs(p.f(p.reference)), 1e-12)

    def test_sign_change_inventory(self):
        self.assertEqual([r["case"] for r in bracketing_rows() if not r["sign_change"]],
                         ["f5-right"])

    def test_bracketed_solvers(self):
        for p in PROBLEMS:
            for solve in (lambda: bisection(p.f, *p.interval),
                          lambda: hybrid(p.f, p.df, *p.interval)):
                with self.subTest(p=p.key, solver=solve):
                    if p.key == "f5-right":
                        with self.assertRaisesRegex(ValueError, "opposite signs"):
                            solve()
                        continue
                    result = solve()
                    self.assertLessEqual(abs(result.root-p.reference), 1e-7)
                    self.assertIn(result.status, ("residual", "bracket"))
                    for earlier, later in zip(result.steps, result.steps[1:]):
                        self.assertLessEqual(later.width, earlier.width*.75000001)

    def test_underflow_cannot_hide_same_sign(self):
        with self.assertRaisesRegex(ValueError, "opposite signs"):
            bisection(lambda x: 1e-300, 0, 1)

    def test_hybrid_recovers_from_flat_midpoint(self):
        p = PROBLEMS[2]
        self.assertEqual(newton(p.f, p.df, 1).status, "unusable derivative")
        result = hybrid(p.f, p.df, *p.interval, tol_f=TARGET, tol_x=None)
        self.assertEqual(result.steps[0].kind, "bisection")
        self.assertTrue(any(s.kind == "newton" for s in result.steps))
        self.assertLessEqual(result.residual, TARGET)

    def test_exact_root_precedes_slope_checks(self):
        p = PROBLEMS[6]
        self.assertEqual(newton(p.f, p.df, 0).iterations, 0)
        self.assertEqual(hybrid(p.f, p.df, 0, .001).iterations, 0)
        self.assertEqual(secant(p.f, 0, 0).iterations, 0)

    def test_secant_equal_values(self):
        self.assertEqual(secant(lambda x: x*x+1, -1, 1).status, "unusable secant slope")

    def test_fixed_point_residual_and_breakdown(self):
        p = PROBLEMS[1]
        result = fixed_point(p.f, math.cos, .5)
        self.assertEqual(result.residual, abs(p.f(result.root)))
        self.assertLessEqual(result.residual, 1e-8)
        failure = fixed_point(p.f, math.acos, .5)
        self.assertGreater(failure.root, 1)
        self.assertGreater(failure.residual, 1e-8)

    def test_benchmark_records_actual_target_and_failure(self):
        rows = list(benchmark_rows())
        self.assertEqual(len(rows), 15)
        failures = [r for r in rows if not r["target_met"]]
        self.assertEqual([(r["case"], r["method"]) for r in failures], [("f3", "Newton")])
        self.assertIsNone(failures[0]["median_us"])
        self.assertTrue(all(r["residual"] <= TARGET for r in rows if r["target_met"]))

    def test_bracket_stop_and_iteration_cap(self):
        self.assertEqual(bisection(lambda x: x-.3, 0, 1, tol_x=.5).status, "bracket")
        self.assertEqual(bisection(lambda x: x-.3, 0, 1, max_iter=1).status, "iteration-limit")

    def test_step_stop_is_distinct_from_residual(self):
        result = fixed_point(lambda x: x-1, lambda x: x, 0)
        self.assertEqual(result.status, "step")
        self.assertEqual(result.residual, 1)


if __name__ == "__main__":
    unittest.main()

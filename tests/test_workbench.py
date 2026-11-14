import csv
from pathlib import Path
from tempfile import NamedTemporaryFile
import unittest

from rootlab.demo import samples
from rootlab.workbench import CASES, export_trace, solve_case


class WorkbenchTests(unittest.TestCase):
    def test_custom_seed_changes_newton_outcome(self):
        failed = solve_case("f3", "Newton")
        solved = solve_case("f3", "Newton", seeds=[0.2], tol_f=1e-10, tol_x=None)
        self.assertEqual(failed.status, "unusable derivative")
        self.assertLessEqual(solved.residual, 1e-10)

    def test_reject_bad_seed_count_and_unavailable_map(self):
        with self.assertRaisesRegex(ValueError, "2 finite"):
            solve_case("f2", "Secant", seeds=[0.5])
        with self.assertRaisesRegex(ValueError, "No fixed-point map"):
            solve_case("f4", "Fixed-point")

    def test_trace_includes_reference_error_and_width(self):
        p = CASES["f3"]
        result = solve_case(p.key, "Hybrid")
        with NamedTemporaryFile(dir=Path.cwd(), suffix=".csv", delete=False) as tmp:
            path = Path(tmp.name)
        try:
            export_trace(path, p, result)
            with path.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
        finally:
            path.unlink()
        self.assertEqual(len(rows), len(result.steps))
        self.assertEqual(float(rows[-1]["reference_error"]), abs(result.root-p.reference))
        self.assertEqual(float(rows[0]["bracket_width"]), 2)

    def test_demo_identifies_wrong_root_and_rejected_bracket(self):
        examples = {(item["case"], item["method"]): item for item in samples()}
        self.assertFalse(examples["f3", "Secant"]["inside"])
        self.assertNotIn("trace", examples["f5-right", "Bisection"])
        self.assertTrue(examples["f3", "Hybrid"]["inside"])


if __name__ == "__main__":
    unittest.main()

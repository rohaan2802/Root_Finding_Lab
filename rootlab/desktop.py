"""Desktop Root Finding Workbench. Launch with python -m rootlab.desktop."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .experiments import METHODS
from .solvers import MAX_ITER, TOL_F, TOL_X
from .workbench import CASES, TRACE_COLUMNS, export_trace, solve_case, trace_rows


class Workbench(ttk.Frame):
    def __init__(self, window):
        super().__init__(window, padding=18)
        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=3)
        self.rowconfigure(6, weight=2)
        self.case = tk.StringVar(value="f3")
        self.method = tk.StringVar(value="Hybrid")
        self.seeds = tk.StringVar()
        self.tol_f = tk.StringVar(value=str(TOL_F))
        self.tol_x = tk.StringVar(value=str(TOL_X))
        self.max_iter = tk.StringVar(value=str(MAX_ITER))
        self.strict = tk.BooleanVar()
        self.summary = tk.StringVar()
        self.case_detail = tk.StringVar()
        self.current = None

        ttk.Label(self, text="Root Finding Workbench", font=("Segoe UI", 22, "bold")).grid(sticky="w")
        toolbar = ttk.Frame(self)
        toolbar.grid(row=1, sticky="ew", pady=(10, 6))
        for column, (label, variable, choices, width) in enumerate((
            ("Equation", self.case, tuple(CASES), 11),
            ("Solver", self.method, METHODS, 13),
            ("Seeds or bounds", self.seeds, None, 15),
            ("Residual tol.", self.tol_f, None, 10),
            ("Step tol.", self.tol_x, None, 10),
            ("Max updates", self.max_iter, None, 9),
        )):
            ttk.Label(toolbar, text=label).grid(row=0, column=column, sticky="w", padx=(0, 9))
            if choices:
                control = ttk.Combobox(toolbar, textvariable=variable, values=choices,
                                       state="readonly", width=width)
                control.bind("<<ComboboxSelected>>", self.update_case)
            else:
                control = ttk.Entry(toolbar, textvariable=variable, width=width)
            control.grid(row=1, column=column, sticky="ew", padx=(0, 9))
        ttk.Label(self, textvariable=self.case_detail, wraplength=790).grid(
            row=2, sticky="w", pady=(0, 6))

        actions = ttk.Frame(self)
        actions.grid(row=3, sticky="ew")
        ttk.Button(actions, text="Run solver", command=self.run).pack(side="left")
        ttk.Checkbutton(actions, text="Residual-only tolerance", variable=self.strict).pack(
            side="left", padx=10)
        self.export_button = ttk.Button(actions, text="Export trace CSV", command=self.export)
        self.export_button.pack(side="right")
        ttk.Label(self, textvariable=self.summary, wraplength=790).grid(row=4, sticky="ew", pady=8)

        fig = Figure(figsize=(8, 3), dpi=100, layout="constrained", facecolor="#f6f4ff")
        self.function_axis, self.error_axis = fig.subplots(1, 2)
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid(row=5, sticky="nsew")

        trace = ttk.Frame(self)
        trace.grid(row=6, sticky="nsew", pady=(9, 0))
        trace.columnconfigure(0, weight=1)
        trace.rowconfigure(0, weight=1)
        self.table = ttk.Treeview(trace, columns=TRACE_COLUMNS, show="headings", height=6)
        for key, label in zip(TRACE_COLUMNS, (
            "Point", "Step", "Estimate x", "f(x)", "Residual", "Reference error", "Width",
        ), strict=True):
            self.table.heading(key, text=label)
            self.table.column(key, minwidth=52, width=96, anchor="center")
        scrollbar = ttk.Scrollbar(trace, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.update_case()
        self.run()

    def update_case(self, _event=None):
        problem = CASES[self.case.get()]
        self.case_detail.set(
            f"f(x) = {problem.equation}    •    Assigned interval {problem.interval}\n"
            "Leave seeds blank for case defaults, or enter space-separated starting points."
        )

    def clear(self):
        self.current = None
        self.export_button.state(["disabled"])
        self.table.delete(*self.table.get_children())
        self.function_axis.clear()
        self.error_axis.clear()

    def run(self):
        self.clear()
        problem = CASES[self.case.get()]
        try:
            seeds = [float(value) for value in self.seeds.get().split()] or None
            result = solve_case(
                problem.key, self.method.get(), seeds=seeds, tol_f=float(self.tol_f.get()),
                tol_x=None if self.strict.get() else float(self.tol_x.get()),
                max_iter=int(self.max_iter.get()),
            )
        except (ValueError, ArithmeticError) as error:
            self.summary.set(f"Cannot run this configuration. {error}")
            self.canvas.draw_idle()
            return

        self.current = problem, result
        self.export_button.state(["!disabled"])
        inside = problem.interval[0] <= result.root <= problem.interval[1]
        self.summary.set(
            f"x = {result.root:.12g}  |  Residual {result.residual:.3e}  |  "
            f"Reference error {abs(result.root-problem.reference):.3e}\n"
            f"{result.iterations} updates  |  {result.status}  |  "
            f"{'Inside' if inside else 'Outside'} assigned interval"
        )
        rows = list(trace_rows(problem, result))
        for row in rows:
            self.table.insert("", "end", values=tuple(
                "—" if value is None else f"{value:.7g}" if isinstance(value, float) else value
                for value in row
            ))
        a, b = problem.interval
        xs = [a + (b-a)*i/240 for i in range(241)]
        self.function_axis.plot(xs, [problem.f(x) for x in xs], color="#5341a6")
        self.function_axis.axhline(0, color="#65718d", linewidth=1)
        self.function_axis.scatter(problem.reference, 0, label="Reference", color="#146b75")
        bracket_points = [step for step in result.steps if a <= step.x <= b]
        if bracket_points:
            self.function_axis.scatter([s.x for s in bracket_points], [s.fx for s in bracket_points],
                                       label="Recorded in interval", s=15, color="#a24b27")
        self.function_axis.set(title="Assigned interval", xlabel="x", ylabel="f(x)")
        self.function_axis.legend(fontsize=8)
        self.error_axis.semilogy([max(row[4], 1e-17) for row in rows], ".-", label="Residual")
        self.error_axis.semilogy([max(row[5], 1e-17) for row in rows], ".-", label="Reference error")
        self.error_axis.set(title="Convergence history", xlabel="Recorded point")
        self.error_axis.grid(alpha=.25)
        self.error_axis.legend(fontsize=8)
        self.canvas.draw_idle()

    def export(self):
        if self.current is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
            initialfile=f"{self.current[0].key}_trace.csv",
        )
        if path:
            try:
                export_trace(path, *self.current)
            except OSError as error:
                messagebox.showerror("Could not save trace", str(error), parent=self)


def main():
    window = tk.Tk()
    window.title("Root Finding Workbench")
    window.geometry("950x760")
    window.minsize(810, 650)
    Workbench(window)
    window.mainloop()


if __name__ == "__main__":
    main()

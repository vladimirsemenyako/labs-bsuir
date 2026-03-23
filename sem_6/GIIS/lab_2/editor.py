import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Tuple, Literal, Any
from dataclasses import dataclass, field

from algorithms import (
    circle_bresenham,
    circle_all_steps,
    ellipse,
    ellipse_all_steps,
    hyperbola,
    hyperbola_steps,
    parabola,
    parabola_steps,
)

CurveKind = Literal["circle", "ellipse", "hyperbola", "parabola"]
CELL = 24
GRID_LIMIT = 32


def grid_to_canvas(x: int, y: int) -> Tuple[int, int]:
    cx = x * CELL + CELL // 2
    cy = (GRID_LIMIT - 1 - y) * CELL + CELL // 2
    return (cx, cy)


def canvas_to_grid(cx: int, cy: int) -> Tuple[int, int]:
    x = cx // CELL
    y = GRID_LIMIT - 1 - (cy // CELL)
    x = max(0, min(GRID_LIMIT - 1, x))
    y = max(0, min(GRID_LIMIT - 1, y))
    return (x, y)


@dataclass
class Curve:
    kind: CurveKind
    params: dict  # cx, cy, r / a,b / a,b,x_max / p,y_max
    points: List[Tuple[int, int]] = field(default_factory=list)
    step_extras: List[dict] = field(default_factory=list)


@dataclass
class DebugCurve:
    curve: Curve
    step_points: List[Tuple[int, int]] = field(default_factory=list)
    step_extra: List[dict] = field(default_factory=list)


class CanvasGrid(tk.Canvas):
    def __init__(self, parent, debug: bool, **kwargs):
        self.debug_mode = debug
        self.curves: List[Curve] = []
        self._curve_kind: CurveKind = "circle"
        self._clicks: List[Tuple[int, int]] = []
        self._step_index: int = -1
        self._step_points: List[Tuple[int, int]] = []
        self._step_extra: List[dict] = []
        self._debug_curve: Optional[DebugCurve] = None
        self._param_a = tk.IntVar(value=5)
        self._param_b = tk.IntVar(value=3)
        self._param_p = tk.IntVar(value=4)
        self._param_x_max = tk.IntVar(value=15)
        self._param_y_max = tk.IntVar(value=10)
        width = GRID_LIMIT * CELL
        height = GRID_LIMIT * CELL
        super().__init__(parent, width=width, height=height, bg="#1e1e2e", **kwargs)
        self._draw_grid()
        self.bind("<Button-1>", self._on_click)
        self.bind("<Motion>", self._on_motion)

    def set_curve_kind(self, kind: CurveKind) -> None:
        self._curve_kind = kind
        self._clicks = []

    def set_debug(self, debug: bool) -> None:
        self.debug_mode = debug
        self._step_index = -1
        self._step_points = []
        self._step_extra = []
        self._debug_curve = None
        self._redraw()

    def _draw_grid(self) -> None:
        self.delete("grid")
        for i in range(GRID_LIMIT + 1):
            self.create_line(i * CELL, 0, i * CELL, GRID_LIMIT * CELL, fill="#45475a", tags="grid")
            self.create_line(0, i * CELL, GRID_LIMIT * CELL, i * CELL, fill="#45475a", tags="grid")
        self.tag_lower("grid")

    def _redraw(self) -> None:
        self.delete("curve")
        self.delete("step")
        self.delete("cursor")
        self._draw_grid()
        for c in self.curves:
            self._draw_curve(c)
        if self.debug_mode and self._debug_curve is not None and self._step_points:
            self._draw_debug_up_to_step()
        elif self.debug_mode and self._step_index >= 0 and self._step_points:
            self._draw_step_highlight()
        for (gx, gy) in self._clicks:
            cx, cy = grid_to_canvas(gx, gy)
            self.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, outline="#f9e2af", width=2, tags="cursor")

    def _draw_curve(self, c: Curve) -> None:
        for (x, y) in c.points:
            if 0 <= x < GRID_LIMIT and 0 <= y < GRID_LIMIT:
                self.create_rectangle(
                    x * CELL, (GRID_LIMIT - 1 - y) * CELL,
                    (x + 1) * CELL, (GRID_LIMIT - 1 - y + 1) * CELL,
                    fill="#89b4fa", outline="#45475a", tags="curve",
                )

    def _draw_debug_up_to_step(self) -> None:
        if self._step_index < 0:
            return
        for i in range(min(self._step_index + 1, len(self._step_points))):
            x, y = self._step_points[i]
            if 0 <= x < GRID_LIMIT and 0 <= y < GRID_LIMIT:
                self.create_rectangle(
                    x * CELL, (GRID_LIMIT - 1 - y) * CELL,
                    (x + 1) * CELL, (GRID_LIMIT - 1 - y + 1) * CELL,
                    fill="#89b4fa", outline="#45475a", tags="step",
                )
        self._draw_step_highlight()

    def _draw_step_highlight(self) -> None:
        if self._step_index < 0 or self._step_index >= len(self._step_points):
            return
        x, y = self._step_points[self._step_index]
        if 0 <= x < GRID_LIMIT and 0 <= y < GRID_LIMIT:
            self.create_rectangle(
                x * CELL, (GRID_LIMIT - 1 - y) * CELL,
                (x + 1) * CELL, (GRID_LIMIT - 1 - y + 1) * CELL,
                fill="#a6e3a1", outline="#89b4fa", width=2, tags="step",
            )

    def _on_click(self, event: tk.Event) -> None:
        gx, gy = canvas_to_grid(event.x, event.y)
        # Начало новой кривой: предыдущую отладочную переносим в список
        if self._debug_curve is not None and (
            (self._curve_kind == "circle" and len(self._clicks) == 0) or
            (self._curve_kind == "ellipse" and len(self._clicks) == 0) or
            (self._curve_kind == "hyperbola" and len(self._clicks) == 0) or
            (self._curve_kind == "parabola" and len(self._clicks) == 0)
        ):
            self.curves.append(self._debug_curve.curve)
            self._debug_curve = None
            self._step_points = []
            self._step_extra = []
            self._step_index = -1
        if self._curve_kind == "circle":
            if len(self._clicks) == 0:
                self._clicks = [(gx, gy)]
            else:
                cx, cy = self._clicks[0]
                r = int(round(((gx - cx) ** 2 + (gy - cy) ** 2) ** 0.5))
                r = max(1, min(r, GRID_LIMIT))
                self._add_curve(cx, cy, r=r)
                self._clicks = []
        elif self._curve_kind == "ellipse":
            if len(self._clicks) == 0:
                self._clicks = [(gx, gy)]
            elif len(self._clicks) == 1:
                self._clicks.append((gx, gy))
            else:
                cx, cy = self._clicks[0]
                a = abs(gx - cx)
                b = abs(cy - gy)
                a, b = max(1, a), max(1, b)
                self._add_curve(cx, cy, a=a, b=b)
                self._clicks = []
        elif self._curve_kind == "hyperbola":
            if len(self._clicks) == 0:
                self._clicks = [(gx, gy)]
            else:
                cx, cy = self._clicks[0]
                a = self._param_a.get()
                b = self._param_b.get()
                x_max = self._param_x_max.get()
                if a < 1:
                    a = 1
                if b < 1:
                    b = 1
                self._add_curve(cx, cy, a=a, b=b, x_max=x_max)
                self._clicks = []
        elif self._curve_kind == "parabola":
            if len(self._clicks) == 0:
                self._clicks = [(gx, gy)]
            else:
                cx, cy = self._clicks[0]
                p = self._param_p.get()
                y_max = self._param_y_max.get()
                if p < 1:
                    p = 1
                self._add_curve(cx, cy, p=p, y_max=y_max)
                self._clicks = []
        self._redraw()

    def _add_curve(self, cx: int, cy: int, **kw) -> None:
        kind = self._curve_kind
        points: List[Tuple[int, int]] = []
        step_pts: List[Tuple[int, int]] = []
        step_ext: List[dict] = []
        if kind == "circle":
            r = kw.get("r", 5)
            points = circle_bresenham(cx, cy, r)
            step_pts, step_ext = circle_all_steps(cx, cy, r)
            params = {"cx": cx, "cy": cy, "r": r}
        elif kind == "ellipse":
            a, b = kw.get("a", 5), kw.get("b", 3)
            points = ellipse(cx, cy, a, b)
            step_pts, step_ext = ellipse_all_steps(cx, cy, a, b)
            params = {"cx": cx, "cy": cy, "a": a, "b": b}
        elif kind == "hyperbola":
            a, b = kw.get("a", 5), kw.get("b", 3)
            x_max = kw.get("x_max", 15)
            points = hyperbola(cx, cy, a, b, x_max)
            step_pts, step_ext = hyperbola_steps(cx, cy, a, b, x_max)
            params = {"cx": cx, "cy": cy, "a": a, "b": b, "x_max": x_max}
        else:  # parabola
            p = kw.get("p", 4)
            y_max = kw.get("y_max", 10)
            points = parabola(cx, cy, p, y_max)
            step_pts, step_ext = parabola_steps(cx, cy, p, y_max)
            params = {"cx": cx, "cy": cy, "p": p, "y_max": y_max}
        curve = Curve(kind=kind, params=params, points=points, step_extras=step_ext)
        if self.debug_mode and (step_pts or step_ext):
            self._debug_curve = DebugCurve(curve=curve, step_points=step_pts, step_extra=step_ext)
            self._step_points = step_pts
            self._step_extra = step_ext
            self._step_index = 0
        else:
            self.curves.append(curve)
        self._redraw()

    def build_from_params(self) -> None:
        """Построить по параметрам из полей (гипербола/парабола: центр уже в _clicks)."""
        if self._curve_kind == "hyperbola" and len(self._clicks) == 1:
            cx, cy = self._clicks[0]
            self._add_curve(cx, cy, a=self._param_a.get(), b=self._param_b.get(), x_max=self._param_x_max.get())
            self._clicks = []
        elif self._curve_kind == "parabola" and len(self._clicks) == 1:
            cx, cy = self._clicks[0]
            self._add_curve(cx, cy, p=self._param_p.get(), y_max=self._param_y_max.get())
            self._clicks = []
        self._redraw()

    def _on_motion(self, event: tk.Event) -> None:
        self._redraw()

    def clear(self) -> None:
        self.curves.clear()
        self._clicks = []
        self._step_index = -1
        self._step_points = []
        self._step_extra = []
        self._debug_curve = None
        self._redraw()

    def step_next(self) -> bool:
        if not self._step_points or self._step_index >= len(self._step_points) - 1:
            return False
        self._step_index += 1
        self._redraw()
        return True

    def step_prev(self) -> bool:
        if self._step_index <= 0:
            return False
        self._step_index -= 1
        self._redraw()
        return True

    def get_step_info(self) -> str:
        if self._step_index < 0 or self._step_index >= len(self._step_points):
            return ""
        parts = [f"Шаг {self._step_index + 1} из {len(self._step_points)}"]
        pt = self._step_points[self._step_index]
        parts.append(f"({pt[0]}, {pt[1]})")
        if self._step_index < len(self._step_extra):
            ex = self._step_extra[self._step_index]
            for k, v in ex.items():
                if v is not None:
                    parts.append(f"{k}={v}")
        return " | ".join(parts)

    def get_full_step_table(self, current_step: Optional[int] = None) -> str:
        if not self._step_points:
            return ""
        n = len(self._step_points)
        current_step = current_step if current_step is not None else self._step_index
        lines: List[str] = []
        kind = self._curve_kind
        if kind == "circle":
            lines.append("Окружность (Брезенхем): Δ = x²+y²−R²; H/V/D — выбор пикселя")
            lines.append("")
            lines.append(f"{'i':>3}   {'Δ':>6}   {'δ':>6}  {'δ*':>6}  пиксель   (x,y)")
            lines.append("-" * 44)
            for i in range(n):
                ex = self._step_extra[i] if i < len(self._step_extra) else {}
                pt = self._step_points[i]
                d = ex.get("Δ", "")
                d2 = ex.get("δ", "")
                d3 = ex.get("δ*", "")
                pix = ex.get("пиксель", "")
                mark = " >>>" if i == current_step else ""
                lines.append(f"{i:>3}   {str(d):>6}   {str(d2):>6}  {str(d3):>6}  {pix:>7}   ({pt[0]},{pt[1]}){mark}")
        elif kind == "ellipse":
            lines.append("Эллипс (Брезенхем): Δ = b²x²+a²y²−a²b²; H/V/D — выбор пикселя")
            lines.append("")
            lines.append(f"{'i':>3}   {'Δ':>8}   δ/δ*    пиксель   (x,y)")
            lines.append("-" * 44)
            for i in range(n):
                ex = self._step_extra[i] if i < len(self._step_extra) else {}
                pt = self._step_points[i]
                d = ex.get("Δ", "")
                pix = ex.get("пиксель", "")
                mark = " >>>" if i == current_step else ""
                lines.append(f"{i:>3}   {str(d):>8}   —       {pix:>7}   ({pt[0]},{pt[1]}){mark}")
        elif kind == "hyperbola":
            lines.append("Гипербола x²/a²−y²/b²=1: F = b²x²−a²y²−a²b²")
            lines.append("")
            lines.append(f"{'i':>3}   x   y   F        (x,y)")
            lines.append("-" * 32)
            for i in range(n):
                ex = self._step_extra[i] if i < len(self._step_extra) else {}
                pt = self._step_points[i]
                xl = ex.get("x", "")
                yl = ex.get("y", "")
                f = ex.get("F", "")
                mark = " >>>" if i == current_step else ""
                lines.append(f"{i:>3}   {xl:>2}  {yl:>2}   {str(f):>6}   ({pt[0]},{pt[1]}){mark}")
        else:  # parabola
            lines.append("Парабола y²=2px: x = y²/(2p)")
            lines.append("")
            lines.append(f"{'i':>3}   y   x      x_точн    (x,y)")
            lines.append("-" * 36)
            for i in range(n):
                ex = self._step_extra[i] if i < len(self._step_extra) else {}
                pt = self._step_points[i]
                yl = ex.get("y", "")
                xl = ex.get("x", "")
                xf = ex.get("x_точн", "")
                mark = " >>>" if i == current_step else ""
                lines.append(f"{i:>3}   {yl:>2}  {xl:>2}   {str(xf):>8}   ({pt[0]},{pt[1]}){mark}")
        return "\n".join(lines)


class CurveEditorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Графический редактор — Линии второго порядка (ЛР №2)")
        self.root.minsize(900, 620)
        self._curve_kind: CurveKind = "circle"
        self._debug = tk.BooleanVar(value=False)
        self._build_ui()

    def _build_ui(self) -> None:
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        menu_curves = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Линии второго порядка", menu=menu_curves)
        menu_curves.add_command(label="Окружность", command=lambda: self._set_kind("circle"))
        menu_curves.add_command(label="Эллипс", command=lambda: self._set_kind("ellipse"))
        menu_curves.add_command(label="Гипербола", command=lambda: self._set_kind("hyperbola"))
        menu_curves.add_command(label="Парабола", command=lambda: self._set_kind("parabola"))
        menu_curves.add_separator()
        menu_curves.add_checkbutton(label="Отладочный режим", variable=self._debug, command=self._on_debug_toggle)
        menu_curves.add_separator()
        menu_curves.add_command(label="Очистить", command=self._on_clear)
        menu_curves.add_command(label="Выход", command=self.root.quit)
        menu_help = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=menu_help)
        menu_help.add_command(label="О программе", command=self._on_about)

        toolbar = ttk.Frame(self.root, padding=4)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(toolbar, text="Линии второго порядка:").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="Окружность", command=lambda: self._set_kind("circle")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Эллипс", command=lambda: self._set_kind("ellipse")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Гипербола", command=lambda: self._set_kind("hyperbola")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Парабола", command=lambda: self._set_kind("parabola")).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Checkbutton(toolbar, text="Отладочный режим", variable=self._debug, command=self._on_debug_toggle).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Очистить", command=self._on_clear).pack(side=tk.LEFT, padx=2)

        main = ttk.Frame(self.root, padding=4)
        main.pack(fill=tk.BOTH, expand=True)
        self.canvas_frame = ttk.Frame(main)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = CanvasGrid(self.canvas_frame, debug=self._debug.get())
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.set_curve_kind(self._curve_kind)

        params_frame = ttk.LabelFrame(main, text="Параметры (гипербола/парабола)", padding=4)
        params_frame.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Label(params_frame, text="Гипербола: a, b, x_max").pack(anchor=tk.W)
        ttk.Label(params_frame, text="a:").pack(anchor=tk.W)
        tk.Spinbox(params_frame, from_=1, to=20, textvariable=self.canvas._param_a, width=8).pack(anchor=tk.W)
        ttk.Label(params_frame, text="b:").pack(anchor=tk.W)
        tk.Spinbox(params_frame, from_=1, to=20, textvariable=self.canvas._param_b, width=8).pack(anchor=tk.W)
        ttk.Label(params_frame, text="x_max:").pack(anchor=tk.W)
        tk.Spinbox(params_frame, from_=1, to=30, textvariable=self.canvas._param_x_max, width=8).pack(anchor=tk.W)
        ttk.Label(params_frame, text="Парабола: p, y_max").pack(anchor=tk.W, pady=(8,0))
        ttk.Label(params_frame, text="p:").pack(anchor=tk.W)
        tk.Spinbox(params_frame, from_=1, to=20, textvariable=self.canvas._param_p, width=8).pack(anchor=tk.W)
        ttk.Label(params_frame, text="y_max:").pack(anchor=tk.W)
        tk.Spinbox(params_frame, from_=1, to=20, textvariable=self.canvas._param_y_max, width=8).pack(anchor=tk.W)
        ttk.Button(params_frame, text="Построить (после 1-го клика)", command=self.canvas.build_from_params).pack(pady=4)

        debug_frame = ttk.LabelFrame(main, text="Отладочный режим — пошаговое решение", padding=4)
        debug_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        self.lbl_step = ttk.Label(debug_frame, text="Включите отладочный режим и постройте кривую.")
        self.lbl_step.pack(anchor=tk.W)
        btn_frame = ttk.Frame(debug_frame)
        btn_frame.pack(fill=tk.X, pady=4)
        ttk.Button(btn_frame, text="← Шаг назад", command=self._step_prev).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Шаг вперёд →", command=self._step_next).pack(side=tk.LEFT, padx=2)
        ttk.Label(debug_frame, text="Ход решения (откуда берутся точки):").pack(anchor=tk.W, pady=(8, 2))
        text_frame = ttk.Frame(debug_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=2)
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._debug_text = tk.Text(
            text_frame, wrap=tk.WORD, width=50, height=22,
            font=("Consolas", 9), bg="#313244", fg="#cdd6f4",
            insertbackground="#cdd6f4", selectbackground="#45475a", relief=tk.FLAT, padx=6, pady=6,
        )
        self._debug_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._debug_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self._debug_text.yview)
        self._update_step_label()

    def _set_kind(self, kind: CurveKind) -> None:
        self._curve_kind = kind
        self.canvas.set_curve_kind(kind)
        self._update_step_label()

    def _on_debug_toggle(self) -> None:
        self.canvas.set_debug(self._debug.get())
        self._update_step_label()

    def _on_clear(self) -> None:
        self.canvas.clear()
        self._update_step_label()

    def _step_next(self) -> None:
        if self.canvas.step_next():
            self._update_step_label()

    def _step_prev(self) -> None:
        if self.canvas.step_prev():
            self._update_step_label()

    def _update_step_label(self) -> None:
        if self._debug.get():
            info = self.canvas.get_step_info()
            self.lbl_step.config(text=info or "Постройте кривую (см. подсказки ниже).")
            table = self.canvas.get_full_step_table()
            self._debug_text.delete("1.0", tk.END)
            if table:
                self._debug_text.insert(tk.END, table)
                try:
                    pos = self._debug_text.search(">>>", "1.0", tk.END)
                    if pos:
                        self._debug_text.see(pos)
                except tk.TclError:
                    pass
            else:
                self._debug_text.insert(
                    tk.END,
                    "Окружность: 2 клика (центр, точка на окружности).\n"
                    "Эллипс: 3 клика (центр, конец a, конец b).\n"
                    "Гипербола: 1 клик (центр), задайте a, b, x_max → Построить.\n"
                    "Парабола: 1 клик (вершина), задайте p, y_max → Построить.\n\n"
                    "Таблица хода появится после построения в отладочном режиме.",
                )
        else:
            self.lbl_step.config(text="Включите отладочный режим и постройте кривую.")
            self._debug_text.delete("1.0", tk.END)
            self._debug_text.insert(
                tk.END,
                "Выберите кривую в меню «Линии второго порядка».\n"
                "Окружность / Эллипс — по кликам. Гипербола / Парабола — параметры слева.",
            )

    def _on_about(self) -> None:
        messagebox.showinfo(
            "О программе",
            "Графический редактор — линии второго порядка.\n\n"
            "Лабораторная работа №2 (Практикум по компьютерной графике, БГУИР).\n\n"
            "Кривые: окружность (Брезенхем), эллипс, гипербола, парабола.\n"
            "Меню и панель «Линии второго порядка». Отладочный режим — пошаговое решение на сетке.",
        )

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = CurveEditorApp()
    app.run()


if __name__ == "__main__":
    main()

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass, field
from tkinter import ttk, messagebox
from typing import List, Literal, Optional, Tuple

from algorithms import bezier_curve, bspline_curve, hermite_curve

Point = Tuple[float, float]
CurveKind = Literal["hermite", "bezier", "bspline"]


@dataclass
class Segment:
    kind: CurveKind
    control_points: List[Point] = field(default_factory=list)


class CurveEditorApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Графический редактор — Параметрические кривые (ЛР №3)")
        self.root.minsize(980, 680)

        self.curve_kind: CurveKind = "bezier"
        self.edit_mode = tk.BooleanVar(value=False)
        self.stitch_mode = tk.BooleanVar(value=False)

        self.segments: List[Segment] = []  # Эрмит/Безье (по 4 точки на сегмент)
        self.bspline_points: List[Point] = []  # общий список опорных точек B-сплайна
        self.pending_points: List[Point] = []

        self.drag_target: Optional[Tuple[str, int, int]] = None  # ("segment"/"bspline", idx, pidx)
        self.drag_radius = 10

        self._build_ui()
        self._update_status()
        self.redraw()

    def _build_ui(self) -> None:
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        menu_curves = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Кривые", menu=menu_curves)
        menu_curves.add_command(label="Эрмита", command=lambda: self.set_kind("hermite"))
        menu_curves.add_command(label="Безье", command=lambda: self.set_kind("bezier"))
        menu_curves.add_command(label="B-сплайн", command=lambda: self.set_kind("bspline"))
        menu_curves.add_separator()
        menu_curves.add_checkbutton(label="Режим корректировки", variable=self.edit_mode, command=self._update_status)
        menu_curves.add_checkbutton(label="Режим стыковки сегментов", variable=self.stitch_mode)
        menu_curves.add_separator()
        menu_curves.add_command(label="Удалить последнюю", command=self.delete_last)
        menu_curves.add_command(label="Очистить", command=self.clear_all)
        menu_curves.add_command(label="Выход", command=self.root.quit)

        menu_help = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=menu_help)
        menu_help.add_command(label="О программе", command=self.show_about)

        toolbar = ttk.Frame(self.root, padding=6)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(toolbar, text="Кривые:").pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(toolbar, text="Эрмита", command=lambda: self.set_kind("hermite")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Безье", command=lambda: self.set_kind("bezier")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="B-сплайн", command=lambda: self.set_kind("bspline")).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Checkbutton(toolbar, text="Корректировка", variable=self.edit_mode, command=self._update_status).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Checkbutton(toolbar, text="Стыковка", variable=self.stitch_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Удалить последнюю", command=self.delete_last).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Очистить", command=self.clear_all).pack(side=tk.LEFT, padx=2)

        main = ttk.Frame(self.root, padding=6)
        main.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main, bg="#1e1e2e", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda _e: self.redraw())
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        side = ttk.LabelFrame(main, text="Состояние", padding=8)
        side.pack(side=tk.RIGHT, fill=tk.Y)
        self.status = ttk.Label(side, text="", justify=tk.LEFT, wraplength=270)
        self.status.pack(anchor=tk.W)
        ttk.Separator(side, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        ttk.Label(side, text="Подсказка по точкам:", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W)
        self.hint = ttk.Label(side, text="", justify=tk.LEFT, wraplength=270)
        self.hint.pack(anchor=tk.W, pady=(4, 0))

    def set_kind(self, kind: CurveKind) -> None:
        self.curve_kind = kind
        self.pending_points = []
        self.drag_target = None
        self._update_status()
        self.redraw()

    def clear_all(self) -> None:
        self.segments.clear()
        self.bspline_points.clear()
        self.pending_points.clear()
        self.drag_target = None
        self.redraw()
        self._update_status()

    def delete_last(self) -> None:
        if self.curve_kind == "bspline":
            if self.bspline_points:
                self.bspline_points.pop()
        else:
            for i in range(len(self.segments) - 1, -1, -1):
                if self.segments[i].kind == self.curve_kind:
                    self.segments.pop(i)
                    break
        self.pending_points.clear()
        self.redraw()
        self._update_status()

    def _last_segment_endpoint(self, kind: CurveKind) -> Optional[Point]:
        for seg in reversed(self.segments):
            if seg.kind != kind:
                continue
            if kind == "hermite":
                return seg.control_points[1]
            if kind == "bezier":
                return seg.control_points[3]
        return None

    def on_left_click(self, event: tk.Event) -> None:
        px, py = float(event.x), float(event.y)
        if self.edit_mode.get():
            self.drag_target = self.find_nearest_control_point(px, py)
            self.redraw()
            return

        if self.curve_kind == "bspline":
            self.bspline_points.append((px, py))
        else:
            if not self.pending_points and self.stitch_mode.get():
                endpoint = self._last_segment_endpoint(self.curve_kind)
                if endpoint is not None:
                    self.pending_points.append(endpoint)
            self.pending_points.append((px, py))
            if len(self.pending_points) == 4:
                self.segments.append(Segment(kind=self.curve_kind, control_points=list(self.pending_points)))
                if self.stitch_mode.get():
                    if self.curve_kind == "hermite":
                        self.pending_points = [self.pending_points[1]]
                    else:
                        self.pending_points = [self.pending_points[3]]
                else:
                    self.pending_points = []

        self.redraw()
        self._update_status()

    def on_drag(self, event: tk.Event) -> None:
        if not self.edit_mode.get() or self.drag_target is None:
            return
        px, py = float(event.x), float(event.y)
        target_type, idx, pidx = self.drag_target
        if target_type == "segment":
            if 0 <= idx < len(self.segments):
                self.segments[idx].control_points[pidx] = (px, py)
        else:
            if 0 <= idx < len(self.bspline_points):
                self.bspline_points[idx] = (px, py)
        self.redraw()

    def on_release(self, _event: tk.Event) -> None:
        self.drag_target = None
        self.redraw()

    def find_nearest_control_point(self, x: float, y: float) -> Optional[Tuple[str, int, int]]:
        best: Optional[Tuple[str, int, int]] = None
        best_dist2 = float(self.drag_radius * self.drag_radius)

        for si, seg in enumerate(self.segments):
            for pi, (px, py) in enumerate(seg.control_points):
                d2 = (px - x) ** 2 + (py - y) ** 2
                if d2 <= best_dist2:
                    best_dist2 = d2
                    best = ("segment", si, pi)

        for pi, (px, py) in enumerate(self.bspline_points):
            d2 = (px - x) ** 2 + (py - y) ** 2
            if d2 <= best_dist2:
                best_dist2 = d2
                best = ("bspline", pi, 0)

        return best

    def redraw(self) -> None:
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.draw_grid(w, h)

        for seg in self.segments:
            if seg.kind == "hermite":
                self.draw_hermite(seg.control_points)
            elif seg.kind == "bezier":
                self.draw_bezier(seg.control_points)

        if len(self.bspline_points) >= 2:
            self.draw_control_polyline(self.bspline_points, "#f9e2af")
        if len(self.bspline_points) >= 4:
            curve = bspline_curve(self.bspline_points, samples_per_segment=70)
            self.draw_curve_polyline(curve, "#89b4fa", width=2)
        self.draw_points(self.bspline_points, "#f38ba8")

        if self.curve_kind in {"hermite", "bezier"} and self.pending_points:
            self.draw_control_polyline(self.pending_points, "#f9e2af", dashed=True)
            self.draw_points(self.pending_points, "#f9e2af")

    def draw_grid(self, width: int, height: int) -> None:
        step = 30
        for x in range(0, width, step):
            self.canvas.create_line(x, 0, x, height, fill="#313244")
        for y in range(0, height, step):
            self.canvas.create_line(0, y, width, y, fill="#313244")

    def draw_curve_polyline(self, points: List[Point], color: str, width: int = 2) -> None:
        if len(points) < 2:
            return
        flat = [coord for p in points for coord in p]
        self.canvas.create_line(*flat, fill=color, width=width, smooth=True)

    def draw_control_polyline(self, points: List[Point], color: str, dashed: bool = False) -> None:
        if len(points) < 2:
            return
        flat = [coord for p in points for coord in p]
        if dashed:
            self.canvas.create_line(*flat, fill=color, width=1, dash=(6, 3))
        else:
            self.canvas.create_line(*flat, fill=color, width=1)

    def draw_points(self, points: List[Point], color: str) -> None:
        for (x, y) in points:
            self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color, outline="#11111b")

    def draw_hermite(self, control_points: List[Point]) -> None:
        self.draw_control_polyline(control_points, "#f9e2af")
        curve = hermite_curve(control_points, samples=200)
        self.draw_curve_polyline(curve, "#89b4fa", width=2)
        if len(control_points) == 4:
            p0, p1, t0, t1 = control_points
            self.draw_points([p0], "#a6e3a1")
            self.draw_points([p1], "#f38ba8")
            self.draw_points([t0, t1], "#fab387")

    def draw_bezier(self, control_points: List[Point]) -> None:
        self.draw_control_polyline(control_points, "#f9e2af")
        curve = bezier_curve(control_points, samples=200)
        self.draw_curve_polyline(curve, "#89b4fa", width=2)
        if len(control_points) == 4:
            self.draw_points([control_points[0]], "#a6e3a1")
            self.draw_points([control_points[3]], "#f38ba8")
            self.draw_points(control_points[1:3], "#fab387")

    def _update_status(self) -> None:
        if self.curve_kind == "hermite":
            kind_name = "Эрмита"
            hint = (
                "4 точки на сегмент:\n"
                "1) начало p0\n2) конец p1\n3) точка касательной в p0\n4) точка касательной в p1"
            )
        elif self.curve_kind == "bezier":
            kind_name = "Безье"
            hint = "4 контрольные точки на сегмент: p0, p1, p2, p3"
        else:
            kind_name = "B-сплайн"
            hint = "Ставьте опорные точки подряд. Сегменты строятся по каждой группе из 4 точек."

        mode = "корректировка" if self.edit_mode.get() else "построение"
        stitch = "вкл" if self.stitch_mode.get() else "выкл"
        text = (
            f"Текущая кривая: {kind_name}\n"
            f"Режим: {mode}\n"
            f"Стыковка сегментов: {stitch}\n\n"
            "Управление:\n"
            "- ЛКМ: добавить точку\n"
            "- В режиме корректировки: ЛКМ + перетаскивание\n"
            "- 'Удалить последнюю' удаляет последний сегмент/точку текущего типа"
        )
        self.status.config(text=text)
        self.hint.config(text=hint)

    def show_about(self) -> None:
        messagebox.showinfo(
            "О программе",
            "Лабораторная работа №3: параметрические кривые.\n\n"
            "Реализованы:\n"
            "- кривая Эрмита\n"
            "- кривая Безье\n"
            "- кубический равномерный B-сплайн\n\n"
            "Есть режим корректировки опорных точек и режим стыковки сегментов.",
        )

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    CurveEditorApp().run()


if __name__ == "__main__":
    main()


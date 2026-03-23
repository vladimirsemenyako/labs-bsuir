from __future__ import annotations

import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List

from algorithms import (
    Vertex4,
    about_point,
    apply_matrix,
    parse_model,
    project_vertices,
    reflection_matrix,
    rotation_x_matrix,
    rotation_y_matrix,
    rotation_z_matrix,
    scaling_matrix,
    translation_matrix,
    vertices_center,
)


class Transform3DApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Графический редактор — 3D преобразования (ЛР №4)")
        self.root.minsize(1040, 720)

        self.vertices_original: List[Vertex4] = []
        self.vertices: List[Vertex4] = []
        self.edges: List[tuple[int, int]] = []

        self.use_perspective = tk.BooleanVar(value=True)
        self.perspective_distance = tk.DoubleVar(value=6.0)
        self.view_scale = tk.DoubleVar(value=120.0)
        self.step_translate = 0.2
        self.step_rotate = 6.0

        self._build_ui()
        self._bind_keys()
        self._load_default_model()
        self._update_status()

    def _build_ui(self) -> None:
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть модель...", command=self.open_model_dialog)
        file_menu.add_command(label="Загрузить demo-куб", command=self._load_default_model)
        file_menu.add_separator()
        file_menu.add_command(label="Сбросить объект", command=self.reset_object)
        file_menu.add_command(label="Выход", command=self.root.quit)

        tr_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Преобразования", menu=tr_menu)
        tr_menu.add_command(label="Сдвиг +X", command=lambda: self.translate(self.step_translate, 0.0, 0.0))
        tr_menu.add_command(label="Сдвиг -X", command=lambda: self.translate(-self.step_translate, 0.0, 0.0))
        tr_menu.add_command(label="Сдвиг +Y", command=lambda: self.translate(0.0, self.step_translate, 0.0))
        tr_menu.add_command(label="Сдвиг -Y", command=lambda: self.translate(0.0, -self.step_translate, 0.0))
        tr_menu.add_separator()
        tr_menu.add_command(label="Поворот X", command=lambda: self.rotate("x", self.step_rotate))
        tr_menu.add_command(label="Поворот Y", command=lambda: self.rotate("y", self.step_rotate))
        tr_menu.add_command(label="Поворот Z", command=lambda: self.rotate("z", self.step_rotate))
        tr_menu.add_separator()
        tr_menu.add_command(label="Масштаб +", command=lambda: self.scale(1.1))
        tr_menu.add_command(label="Масштаб -", command=lambda: self.scale(0.9))
        tr_menu.add_separator()
        tr_menu.add_command(label="Отражение OYZ", command=lambda: self.reflect("OYZ"))
        tr_menu.add_command(label="Отражение OXZ", command=lambda: self.reflect("OXZ"))
        tr_menu.add_command(label="Отражение OXY", command=lambda: self.reflect("OXY"))

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

        toolbar = ttk.Frame(self.root, padding=6)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(toolbar, text="Открыть", command=self.open_model_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Сброс", command=self.reset_object).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Button(toolbar, text="Rx", command=lambda: self.rotate("x", self.step_rotate)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Ry", command=lambda: self.rotate("y", self.step_rotate)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Rz", command=lambda: self.rotate("z", self.step_rotate)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="S+", command=lambda: self.scale(1.1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="S-", command=lambda: self.scale(0.9)).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(
            toolbar,
            text="Перспектива",
            variable=self.use_perspective,
            command=self.redraw,
        ).pack(side=tk.LEFT, padx=(12, 4))
        ttk.Label(toolbar, text="d:").pack(side=tk.LEFT, padx=(8, 2))
        ttk.Spinbox(
            toolbar,
            from_=1.0,
            to=30.0,
            increment=0.5,
            textvariable=self.perspective_distance,
            width=6,
            command=self.redraw,
        ).pack(side=tk.LEFT)
        ttk.Label(toolbar, text="scale:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Spinbox(
            toolbar,
            from_=20.0,
            to=260.0,
            increment=10.0,
            textvariable=self.view_scale,
            width=6,
            command=self.redraw,
        ).pack(side=tk.LEFT)

        main = ttk.Frame(self.root, padding=6)
        main.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main, bg="#1e1e2e", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda _e: self.redraw())

        side = ttk.LabelFrame(main, text="Управление", padding=8)
        side.pack(side=tk.RIGHT, fill=tk.Y)
        self.status = ttk.Label(side, text="", justify=tk.LEFT, wraplength=300)
        self.status.pack(anchor=tk.W)
        ttk.Separator(side, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        self.keys_help = ttk.Label(
            side,
            justify=tk.LEFT,
            text=(
                "Клавиши:\n"
                "←/→/↑/↓  — перенос по X/Y\n"
                "PgUp/PgDn — перенос по Z\n"
                "x/X, y/Y, z/Z — поворот ±\n"
                "+ / - — масштаб\n"
                "1/2/3 — отражение OYZ/OXZ/OXY\n"
                "p — перспектива вкл/выкл\n"
                "r — сброс объекта"
            ),
        )
        self.keys_help.pack(anchor=tk.W)

    def _bind_keys(self) -> None:
        self.root.bind("<Key>", self.on_key)
        self.root.focus_set()

    def _load_default_model(self) -> None:
        model_path = Path(__file__).resolve().parent / "models" / "cube.txt"
        self.load_model(str(model_path))

    def open_model_dialog(self) -> None:
        filename = filedialog.askopenfilename(
            title="Выберите файл модели",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=os.path.dirname(__file__),
        )
        if filename:
            self.load_model(filename)

    def load_model(self, path: str) -> None:
        try:
            vertices, edges = parse_model(path)
        except Exception as exc:
            messagebox.showerror("Ошибка чтения", f"Не удалось прочитать модель:\n{exc}")
            return

        self.vertices_original = list(vertices)
        self.vertices = list(vertices)
        self.edges = list(edges)
        self.redraw()
        self._update_status(extra=f"Модель: {os.path.basename(path)}")

    def apply_transform(self, matrix: List[List[float]]) -> None:
        if not self.vertices:
            return
        self.vertices = apply_matrix(self.vertices, matrix)
        self.redraw()
        self._update_status()

    def translate(self, tx: float, ty: float, tz: float) -> None:
        self.apply_transform(translation_matrix(tx, ty, tz))

    def rotate(self, axis: str, angle: float) -> None:
        if not self.vertices:
            return
        center = vertices_center(self.vertices)
        if axis == "x":
            m = rotation_x_matrix(angle)
        elif axis == "y":
            m = rotation_y_matrix(angle)
        else:
            m = rotation_z_matrix(angle)
        self.apply_transform(about_point(m, center))

    def scale(self, factor: float) -> None:
        if not self.vertices:
            return
        center = vertices_center(self.vertices)
        m = about_point(scaling_matrix(factor, factor, factor), center)
        self.apply_transform(m)

    def reflect(self, plane: str) -> None:
        self.apply_transform(reflection_matrix(plane))

    def reset_object(self) -> None:
        self.vertices = list(self.vertices_original)
        self.redraw()
        self._update_status(extra="Объект сброшен к исходному состоянию")

    def on_key(self, event: tk.Event) -> None:
        key = event.keysym
        ch = event.char

        if key == "Left":
            self.translate(-self.step_translate, 0.0, 0.0)
            return
        if key == "Right":
            self.translate(self.step_translate, 0.0, 0.0)
            return
        if key == "Up":
            self.translate(0.0, self.step_translate, 0.0)
            return
        if key == "Down":
            self.translate(0.0, -self.step_translate, 0.0)
            return
        if key == "Prior":  # PgUp
            self.translate(0.0, 0.0, self.step_translate)
            return
        if key == "Next":  # PgDn
            self.translate(0.0, 0.0, -self.step_translate)
            return

        if ch == "x":
            self.rotate("x", self.step_rotate)
            return
        if ch == "X":
            self.rotate("x", -self.step_rotate)
            return
        if ch == "y":
            self.rotate("y", self.step_rotate)
            return
        if ch == "Y":
            self.rotate("y", -self.step_rotate)
            return
        if ch == "z":
            self.rotate("z", self.step_rotate)
            return
        if ch == "Z":
            self.rotate("z", -self.step_rotate)
            return

        if ch in {"+", "="}:
            self.scale(1.1)
            return
        if ch in {"-", "_"}:
            self.scale(0.9)
            return
        if ch == "1":
            self.reflect("OYZ")
            return
        if ch == "2":
            self.reflect("OXZ")
            return
        if ch == "3":
            self.reflect("OXY")
            return
        if ch in {"p", "P"}:
            self.use_perspective.set(not self.use_perspective.get())
            self.redraw()
            self._update_status()
            return
        if ch in {"r", "R"}:
            self.reset_object()

    def world_to_screen(self, x: float, y: float, canvas_w: float, canvas_h: float) -> tuple[float, float]:
        cx = canvas_w / 2.0
        cy = canvas_h / 2.0
        s = self.view_scale.get()
        return (cx + x * s, cy - y * s)

    def redraw(self) -> None:
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.draw_grid(w, h)
        self.draw_axes(w, h)

        if not self.vertices or not self.edges:
            return

        projected = project_vertices(
            self.vertices,
            use_perspective=self.use_perspective.get(),
            distance=self.perspective_distance.get(),
        )
        pts2d = [self.world_to_screen(x, y, w, h) for (x, y, _z) in projected]

        for i, j in self.edges:
            if i < 0 or j < 0 or i >= len(pts2d) or j >= len(pts2d):
                continue
            x1, y1 = pts2d[i]
            x2, y2 = pts2d[j]
            self.canvas.create_line(x1, y1, x2, y2, fill="#89b4fa", width=2)

        for x, y in pts2d:
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#f38ba8", outline="")

    def draw_grid(self, width: int, height: int) -> None:
        step = 40
        for x in range(0, width, step):
            self.canvas.create_line(x, 0, x, height, fill="#313244")
        for y in range(0, height, step):
            self.canvas.create_line(0, y, width, y, fill="#313244")

    def draw_axes(self, width: int, height: int) -> None:
        cx = width / 2
        cy = height / 2
        self.canvas.create_line(0, cy, width, cy, fill="#585b70", width=1)
        self.canvas.create_line(cx, 0, cx, height, fill="#585b70", width=1)
        self.canvas.create_text(width - 14, cy - 10, text="X", fill="#bac2de")
        self.canvas.create_text(cx + 10, 12, text="Y", fill="#bac2de")

    def _update_status(self, extra: str = "") -> None:
        mode = "перспективная" if self.use_perspective.get() else "ортографическая"
        text = (
            f"Проекция: {mode}\n"
            f"d: {self.perspective_distance.get():.2f}\n"
            f"Масштаб вида: {self.view_scale.get():.1f}\n"
            f"Вершин: {len(self.vertices)}\n"
            f"Рёбер: {len(self.edges)}"
        )
        if extra:
            text = f"{text}\n\n{extra}"
        self.status.config(text=text)

    def show_about(self) -> None:
        messagebox.showinfo(
            "О программе",
            "Лабораторная работа №4: геометрические преобразования 3D-объекта.\n\n"
            "Реализованы:\n"
            "- чтение объекта из txt-файла\n"
            "- перенос, поворот, масштабирование\n"
            "- отражение относительно координатных плоскостей\n"
            "- перспективная и ортографическая проекции\n"
            "- управление преобразованиями с клавиатуры\n\n"
            "Все преобразования выполняются через матрицы 4x4\n"
            "в однородных координатах.",
        )

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    Transform3DApp().run()


if __name__ == "__main__":
    main()


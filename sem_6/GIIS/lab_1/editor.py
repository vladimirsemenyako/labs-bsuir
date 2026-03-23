# -*- coding: utf-8 -*-
"""
Элементарный графический редактор — построение отрезков.
ЛР №1: ЦДА, Брезенхем, Ву. Меню и панель «Отрезки», отладочный режим на дискретной сетке.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Tuple, Literal
from dataclasses import dataclass, field

from algorithms import (
    dda,
    bresenham,
    wu,
    dda_steps,
    bresenham_steps,
    wu_steps,
    Point,
    PointWithIntensity,
)

Algorithm = Literal["dda", "bresenham", "wu"]
CELL = 24  # размер ячейки сетки в пикселях
GRID_LIMIT = 32  # число клеток по одной оси (сетка 32x32)


@dataclass
class Segment:
    x1: int
    y1: int
    x2: int
    y2: int
    algorithm: Algorithm


# Для отладочного режима: последний отрезок рисуем пошагово
@dataclass
class DebugSegment:
    seg: Segment
    step_points: List = field(default_factory=list)
    step_extra: List = field(default_factory=list)


def grid_to_canvas(x: int, y: int) -> Tuple[int, int]:
    """Координаты сетки (0..GRID_LIMIT-1) в пиксели холста (центр клетки)."""
    cx = x * CELL + CELL // 2
    cy = (GRID_LIMIT - 1 - y) * CELL + CELL // 2
    return (cx, cy)


def canvas_to_grid(cx: int, cy: int) -> Tuple[int, int]:
    """Пиксели холста в координаты сетки."""
    x = cx // CELL
    y = GRID_LIMIT - 1 - (cy // CELL)
    x = max(0, min(GRID_LIMIT - 1, x))
    y = max(0, min(GRID_LIMIT - 1, y))
    return (x, y)


class CanvasGrid(tk.Canvas):
    """Холст с дискретной сеткой и рисованием отрезков."""

    def __init__(self, parent, debug: bool, **kwargs):
        self.debug_mode = debug
        self.segments: List[Segment] = []
        self._current_start: Optional[Tuple[int, int]] = None
        self._algorithm: Algorithm = "bresenham"
        self._step_index: int = -1
        self._step_points: List = []
        self._step_extra: List = []
        self._debug_segment: Optional[DebugSegment] = None  # последний отрезок в отладке
        width = GRID_LIMIT * CELL
        height = GRID_LIMIT * CELL
        super().__init__(parent, width=width, height=height, bg="#1e1e2e", **kwargs)
        self._draw_grid()
        self.bind("<Button-1>", self._on_click)
        self.bind("<Motion>", self._on_motion)

    def set_algorithm(self, alg: Algorithm) -> None:
        self._algorithm = alg

    def set_debug(self, debug: bool) -> None:
        self.debug_mode = debug
        self._step_index = -1
        self._step_points = []
        self._step_extra = []
        self._debug_segment = None
        self._redraw()

    def _draw_grid(self) -> None:
        self.delete("grid")
        for i in range(GRID_LIMIT + 1):
            self.create_line(
                i * CELL, 0, i * CELL, GRID_LIMIT * CELL, fill="#45475a", tags="grid"
            )
            self.create_line(
                0, i * CELL, GRID_LIMIT * CELL, i * CELL, fill="#45475a", tags="grid"
            )
        self.tag_lower("grid")

    def _redraw(self) -> None:
        self.delete("segment")
        self.delete("segment_wu")
        self.delete("step")
        self.delete("cursor")
        self._draw_grid()
        for seg in self.segments:
            self._draw_segment(seg)
        # В отладке: последний отрезок рисуем только до текущего шага
        if self.debug_mode and self._debug_segment is not None and self._step_points:
            self._draw_debug_segment_up_to_step()
        elif self.debug_mode and self._step_index >= 0 and self._step_points:
            self._draw_step()
        if self._current_start is not None:
            x, y = self._current_start
            cx, cy = grid_to_canvas(x, y)
            self.create_oval(
                cx - 4, cy - 4, cx + 4, cy + 4, outline="#89b4fa", width=2, tags="cursor"
            )

    def _draw_segment(self, seg: Segment) -> None:
        if seg.algorithm == "wu":
            pts = wu(seg.x1, seg.y1, seg.x2, seg.y2)
            for (x, y, intensity) in pts:
                cx, cy = grid_to_canvas(x, y)
                grey = int(255 * intensity)
                color = "#%02x%02x%02x" % (grey, grey, grey)
                self.create_rectangle(
                    x * CELL,
                    (GRID_LIMIT - 1 - y) * CELL,
                    (x + 1) * CELL,
                    (GRID_LIMIT - 1 - y + 1) * CELL,
                    fill=color,
                    outline="",
                    tags="segment_wu",
                )
        else:
            pts = dda(seg.x1, seg.y1, seg.x2, seg.y2) if seg.algorithm == "dda" else bresenham(seg.x1, seg.y1, seg.x2, seg.y2)
            for (x, y) in pts:
                cx, cy = grid_to_canvas(x, y)
                self.create_rectangle(
                    x * CELL,
                    (GRID_LIMIT - 1 - y) * CELL,
                    (x + 1) * CELL,
                    (GRID_LIMIT - 1 - y + 1) * CELL,
                    fill="#89b4fa",
                    outline="#45475a",
                    tags="segment",
                )

    def _draw_debug_segment_up_to_step(self) -> None:
        """Рисуем последний отрезок только до текущего шага (включительно)."""
        if self._step_index < 0:
            return
        for i in range(self._step_index + 1):
            step_data = self._step_points[i]
            if self._algorithm == "wu":
                for p in step_data:
                    x, y, intensity = p
                    grey = int(255 * intensity)
                    color = "#%02x%02x%02x" % (grey, grey, grey)
                    self.create_rectangle(
                        x * CELL,
                        (GRID_LIMIT - 1 - y) * CELL,
                        (x + 1) * CELL,
                        (GRID_LIMIT - 1 - y + 1) * CELL,
                        fill=color,
                        outline="#45475a",
                        tags="step",
                    )
            else:
                (x, y) = step_data[0]
                self.create_rectangle(
                    x * CELL,
                    (GRID_LIMIT - 1 - y) * CELL,
                    (x + 1) * CELL,
                    (GRID_LIMIT - 1 - y + 1) * CELL,
                    fill="#89b4fa",
                    outline="#a6e3a1",
                    width=1,
                    tags="step",
                )
        # Подсветка текущего шага
        if self._step_index < len(self._step_points):
            self._draw_step()

    def _draw_step(self) -> None:
        """Подсвечиваем текущий шаг (зелёная обводка)."""
        if self._step_index < 0 or self._step_index >= len(self._step_points):
            return
        step_data = self._step_points[self._step_index]
        if self._algorithm == "wu":
            for p in step_data:
                x, y, _ = p
                self.create_rectangle(
                    x * CELL,
                    (GRID_LIMIT - 1 - y) * CELL,
                    (x + 1) * CELL,
                    (GRID_LIMIT - 1 - y + 1) * CELL,
                    outline="#a6e3a1",
                    width=2,
                    tags="step",
                )
        else:
            (x, y) = step_data[0]
            self.create_rectangle(
                x * CELL,
                (GRID_LIMIT - 1 - y) * CELL,
                (x + 1) * CELL,
                (GRID_LIMIT - 1 - y + 1) * CELL,
                fill="#a6e3a1",
                outline="#89b4fa",
                width=2,
                tags="step",
            )

    def _on_click(self, event: tk.Event) -> None:
        gx, gy = canvas_to_grid(event.x, event.y)
        if self._current_start is None:
            # Начало нового отрезка: предыдущий отладочный переносим в список
            if self._debug_segment is not None:
                self.segments.append(self._debug_segment.seg)
                self._debug_segment = None
                self._step_points = []
                self._step_extra = []
                self._step_index = -1
            self._current_start = (gx, gy)
            self._redraw()
            return
        x1, y1 = self._current_start
        x2, y2 = gx, gy
        seg = Segment(x1=x1, y1=y1, x2=x2, y2=y2, algorithm=self._algorithm)
        if self.debug_mode:
            self._build_step_lists(x1, y1, x2, y2)
            self._debug_segment = DebugSegment(
                seg=seg,
                step_points=list(self._step_points),
                step_extra=list(self._step_extra),
            )
            self._step_index = 0
        else:
            self.segments.append(seg)
        self._current_start = None
        self._redraw()

    def _build_step_lists(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self._step_points = []
        self._step_extra = []
        if self._algorithm == "dda":
            for pt, xc, yc in dda_steps(x1, y1, x2, y2):
                self._step_points.append([pt])
                self._step_extra.append({"x": xc, "y": yc})
        elif self._algorithm == "bresenham":
            for pt, e in bresenham_steps(x1, y1, x2, y2):
                self._step_points.append([pt])
                self._step_extra.append({"e": e})
        else:
            for t in wu_steps(x1, y1, x2, y2):
                self._step_points.append(list(t))
                self._step_extra.append({})

    def _on_motion(self, event: tk.Event) -> None:
        self._redraw()

    def clear(self) -> None:
        self.segments.clear()
        self._current_start = None
        self._step_index = -1
        self._step_points = []
        self._step_extra = []
        self._debug_segment = None
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
        step_data = self._step_points[self._step_index]
        extra = self._step_extra[self._step_index] if self._step_index < len(self._step_extra) else {}
        parts = [f"Шаг {self._step_index + 1} из {len(self._step_points)}"]
        if self._algorithm == "dda" and "x" in extra:
            parts.append(f"x={extra['x']:.2f} y={extra['y']:.2f}")
        elif self._algorithm == "bresenham" and "e" in extra and extra["e"] is not None:
            parts.append(f"e={extra['e']}")
        if step_data:
            if self._algorithm == "wu":
                parts.append(" ".join(f"({p[0]},{p[1]}) I={p[2]:.2f}" for p in step_data))
            else:
                parts.append(f"({step_data[0][0]}, {step_data[0][1]})")
        return " | ".join(parts)

    def get_full_step_table(self, current_step: Optional[int] = None) -> str:
        """
        Формирует полную таблицу хода решения для отображения справа.
        current_step — индекс текущего шага (0-based), для отметки «>>>».
        """
        if not self._step_points:
            return ""
        n = len(self._step_points)
        current_step = current_step if current_step is not None else self._step_index
        lines: List[str] = []

        if self._algorithm == "dda":
            lines.append("ЦДА:  x, y — вещ. координаты; Plot — пиксель на сетке")
            lines.append("")
            lines.append(f"{'i':>3}  {'x':>8}  {'y':>8}   Plot(x,y)")
            lines.append("-" * 32)
            for i in range(n):
                extra = self._step_extra[i] if i < len(self._step_extra) else {}
                xc = extra.get("x", 0)
                yc = extra.get("y", 0)
                pt = self._step_points[i][0]
                mark = " >>>" if i == current_step else ""
                lines.append(f"{i:>3}  {xc:>8.2f}  {yc:>8.2f}   ({pt[0]}, {pt[1]}){mark}")
            lines.append("")
            lines.append("Формулы: dx=(x2-x1)/L, dy=(y2-y1)/L; x+=dx, y+=dy; Plot(round(x),round(y))")

        elif self._algorithm == "bresenham":
            lines.append("Брезенхем: e — ошибка (знак решает: сдвигать y или нет)")
            lines.append("")
            lines.append(f"{'i':>3}   {'e':>5}   x   y   Plot(x,y)")
            lines.append("-" * 32)
            for i in range(n):
                extra = self._step_extra[i] if i < len(self._step_extra) else {}
                e = extra.get("e", "")
                e_str = str(e) if e != "" else "—"
                pt = self._step_points[i][0]
                mark = " >>>" if i == current_step else ""
                lines.append(f"{i:>3}   {e_str:>5}   {pt[0]:>2}  {pt[1]:>2}   ({pt[0]}, {pt[1]}){mark}")
            lines.append("")
            lines.append("Начало: e = 2*Δy − Δx. Шаг: если e≥0 → y+=sy, e−=2*Δx; e+=2*Δy; x+=sx")

        else:  # wu
            lines.append("Ву: на каждом шаге два пикселя, интенсивности в сумме = 1")
            lines.append("")
            lines.append(f"{'i':>3}   Пиксели и интенсивности")
            lines.append("-" * 40)
            for i in range(n):
                step_data = self._step_points[i]
                parts = [f"({p[0]},{p[1]}) I={p[2]:.2f}" for p in step_data]
                mark = " >>>" if i == current_step else ""
                lines.append(f"{i:>3}   {'  '.join(parts)}{mark}")
            lines.append("")
            lines.append("Интенсивность = расстояние до идеальной линии (дробная часть)")

        return "\n".join(lines)


class SegmentEditorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Графический редактор — Отрезки (ЛР №1)")
        self.root.minsize(800, 600)
        self._algorithm: Algorithm = "bresenham"
        self._debug = tk.BooleanVar(value=False)
        self._build_ui()

    def _build_ui(self) -> None:
        # Меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        menu_segments = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Отрезки", menu=menu_segments)
        menu_segments.add_command(label="ЦДА", command=lambda: self._set_alg("dda"))
        menu_segments.add_command(
            label="Брезенхем (целочисленный)",
            command=lambda: self._set_alg("bresenham"),
        )
        menu_segments.add_command(label="Ву (сглаживание)", command=lambda: self._set_alg("wu"))
        menu_segments.add_separator()
        menu_segments.add_checkbutton(
            label="Отладочный режим",
            variable=self._debug,
            command=self._on_debug_toggle,
        )
        menu_segments.add_separator()
        menu_segments.add_command(label="Очистить", command=self._on_clear)
        menu_segments.add_command(label="Выход", command=self.root.quit)
        menu_help = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=menu_help)
        menu_help.add_command(label="О программе", command=self._on_about)

        # Панель инструментов «Отрезки»
        toolbar = ttk.Frame(self.root, padding=4)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(toolbar, text="Отрезки:").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="ЦДА", command=lambda: self._set_alg("dda")).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            toolbar, text="Брезенхем", command=lambda: self._set_alg("bresenham")
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Ву", command=lambda: self._set_alg("wu")).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        self._cb_debug = ttk.Checkbutton(
            toolbar, text="Отладочный режим", variable=self._debug, command=self._on_debug_toggle
        )
        self._cb_debug.pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Очистить", command=self._on_clear).pack(
            side=tk.LEFT, padx=2
        )

        # Область холста и отладочная панель
        main = ttk.Frame(self.root, padding=4)
        main.pack(fill=tk.BOTH, expand=True)
        self.canvas_frame = ttk.Frame(main)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = CanvasGrid(
            self.canvas_frame, debug=self._debug.get()
        )
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.set_algorithm(self._algorithm)

        # Отладочная панель (шаги + полная таблица хода решения)
        debug_frame = ttk.LabelFrame(main, text="Отладочный режим — пошаговое решение", padding=4)
        debug_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        self.lbl_step = ttk.Label(debug_frame, text="Включите отладочный режим и постройте отрезок.")
        self.lbl_step.pack(anchor=tk.W)
        btn_frame = ttk.Frame(debug_frame)
        btn_frame.pack(fill=tk.X, pady=4)
        ttk.Button(btn_frame, text="← Шаг назад", command=self._step_prev).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Шаг вперёд →", command=self._step_next).pack(side=tk.LEFT, padx=2)
        ttk.Label(debug_frame, text="Ход решения (откуда берутся точки):").pack(anchor=tk.W, pady=(8, 2))
        # Таблица хода решения с прокруткой
        text_frame = ttk.Frame(debug_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=2)
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._debug_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            width=48,
            height=22,
            font=("Consolas", 10),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            selectbackground="#45475a",
            relief=tk.FLAT,
            padx=6,
            pady=6,
        )
        self._debug_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._debug_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self._debug_text.yview)
        self._update_step_label()

    def _set_alg(self, alg: Algorithm) -> None:
        self._algorithm = alg
        self.canvas.set_algorithm(alg)
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
            self.lbl_step.config(text=info or "Постройте отрезок (два клика).")
            # Полная таблица хода решения справа
            table = self.canvas.get_full_step_table()
            self._debug_text.delete("1.0", tk.END)
            if table:
                self._debug_text.insert(tk.END, table)
                # Прокрутить к текущему шагу (отмеченному >>>)
                self._debug_text.see(tk.END)
                try:
                    # Найти строку с >>> и прокрутить к ней
                    pos = self._debug_text.search(">>>", "1.0", tk.END)
                    if pos:
                        self._debug_text.see(pos)
                except tk.TclError:
                    pass
            else:
                self._debug_text.insert(
                    tk.END,
                    "Постройте отрезок: два клика по сетке\n(начало и конец).\n\n"
                    "Таблица появится здесь с пояснением,\nоткуда берётся каждая точка.",
                )
        else:
            self.lbl_step.config(text="Включите отладочный режим и постройте отрезок.")
            self._debug_text.delete("1.0", tk.END)
            self._debug_text.insert(
                tk.END,
                "Включите «Отладочный режим» и постройте отрезок\n(два клика). Справа появится полная таблица:\n"
                "• ЦДА: x, y (вещ.), Plot(x,y)\n"
                "• Брезенхем: e, x, y, Plot(x,y)\n"
                "• Ву: пиксели и интенсивности.",
            )

    def _on_about(self) -> None:
        messagebox.showinfo(
            "О программе",
            "Графический редактор — построение отрезков.\n\n"
            "Лабораторная работа №1 (Практикум по компьютерной графике, БГУИР).\n\n"
            "Алгоритмы: ЦДА, целочисленный Брезенхем, Ву (сглаживание).\n"
            "Выбор — меню и панель «Отрезки». Отладочный режим — пошаговое решение на дискретной сетке.\n\n"
            "Инструкция: выберите алгоритм, при необходимости включите отладочный режим,\n"
            "затем кликните по сетке дважды (начало и конец отрезка).",
        )

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = SegmentEditorApp()
    app.run()


if __name__ == "__main__":
    main()

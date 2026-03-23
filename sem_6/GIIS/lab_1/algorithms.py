# -*- coding: utf-8 -*-
"""
Алгоритмы построения отрезков в растр.
Лабораторная работа №1, Практикум по компьютерной графике (Самодумкин и др.).
Реализованы: ЦДА, целочисленный Брезенхем, алгоритм Ву (сглаживание).
"""

from __future__ import annotations

import math
from typing import List, Tuple, Iterator, Optional

# Типы: обычная точка и точка с интенсивностью (для Ву)
Point = Tuple[int, int]
PointWithIntensity = Tuple[int, int, float]


def _sign(x: float) -> int:
    """Возвращает -1, 0 или 1 в зависимости от знака x."""
    if x < 0:
        return -1
    if x > 0:
        return 1
    return 0


def _ipart(x: float) -> int:
    """Целая часть числа."""
    return int(math.floor(x))


def _round(x: float) -> int:
    """Округление (для ЦДА по пособию — округляем)."""
    return int(round(x))


# ---------------------------------------------------------------------------
# Цифровой дифференциальный анализатор (ЦДА)
# ---------------------------------------------------------------------------


def dda(x1: int, y1: int, x2: int, y2: int) -> List[Point]:
    """
    Разложение отрезка в растр методом ЦДА.
    Возвращает список целочисленных координат (x, y) пикселей.
    """
    points: List[Point] = []
    length = max(abs(x2 - x1), abs(y2 - y1))
    if length == 0:
        points.append((x1, y1))
        return points

    dx = (x2 - x1) / length
    dy = (y2 - y1) / length
    x = x1 + 0.5 * _sign(dx)
    y = y1 + 0.5 * _sign(dy)
    points.append((_round(x), _round(y)))

    for _ in range(length):
        x += dx
        y += dy
        points.append((_round(x), _round(y)))
    return points


def dda_steps(
    x1: int, y1: int, x2: int, y2: int
) -> Iterator[Tuple[Point, Optional[float], Optional[float]]]:
    """
    Пошаговое выполнение ЦДА для отладочного режима.
    Yields: ( (x, y), x_curr, y_curr ) — отображаемая точка и текущие вещественные координаты.
    """
    length = max(abs(x2 - x1), abs(y2 - y1))
    if length == 0:
        yield ((x1, y1), float(x1), float(y1))
        return

    dx = (x2 - x1) / length
    dy = (y2 - y1) / length
    x = x1 + 0.5 * _sign(dx)
    y = y1 + 0.5 * _sign(dy)
    yield ((_round(x), _round(y)), x, y)

    for _ in range(length):
        x += dx
        y += dy
        yield ((_round(x), _round(y)), x, y)


# ---------------------------------------------------------------------------
# Целочисленный алгоритм Брезенхема
# ---------------------------------------------------------------------------


def _bresenham_first_octant(
    x1: int, y1: int, dx: int, dy: int, sx: int, sy: int
) -> List[Tuple[Point, Optional[int]]]:
    """
    Брезенхем для первого октанта (0 <= dy <= dx, dx > 0).
    Возвращает список ((x, y), e) для отладки; e — ошибка после шага.
    """
    points_with_e: List[Tuple[Point, Optional[int]]] = []
    e = 2 * dy - dx
    x, y = x1, y1
    for _ in range(dx + 1):
        points_with_e.append(((x, y), e))
        if e >= 0:
            y += sy
            e -= 2 * dx
        e += 2 * dy
        x += sx
    return points_with_e


def bresenham(x1: int, y1: int, x2: int, y2: int) -> List[Point]:
    """
    Целочисленный алгоритм Брезенхема для отрезка во всех октантах.
    Возвращает список пикселей (x, y).
    """
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    if dx >= dy:
        # Движение по x
        e = 2 * dy - dx
        x, y = x1, y1
        points: List[Point] = []
        for _ in range(dx + 1):
            points.append((x, y))
            if e >= 0:
                y += sy
                e -= 2 * dx
            e += 2 * dy
            x += sx
        return points
    else:
        # Движение по y (поменяли ролями x и y)
        e = 2 * dx - dy
        x, y = x1, y1
        points = []
        for _ in range(dy + 1):
            points.append((x, y))
            if e >= 0:
                x += sx
                e -= 2 * dy
            e += 2 * dx
            y += sy
        return points


def bresenham_steps(
    x1: int, y1: int, x2: int, y2: int
) -> Iterator[Tuple[Point, Optional[int]]]:
    """
    Пошаговое выполнение Брезенхема для отладочного режима.
    Yields: ( (x, y), e ) — пиксель и текущая ошибка.
    """
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    if dx >= dy:
        e = 2 * dy - dx
        x, y = x1, y1
        for _ in range(dx + 1):
            yield ((x, y), e)
            if e >= 0:
                y += sy
                e -= 2 * dx
            e += 2 * dy
            x += sx
    else:
        e = 2 * dx - dy
        x, y = x1, y1
        for _ in range(dy + 1):
            yield ((x, y), e)
            if e >= 0:
                x += sx
                e -= 2 * dy
            e += 2 * dx
            y += sy


# ---------------------------------------------------------------------------
# Алгоритм Ву (Xiaolin Wu) — сглаживание (anti-aliasing)
# ---------------------------------------------------------------------------


def _fpart(x: float) -> float:
    """Дробная часть, в [0, 1)."""
    return x - math.floor(x)


def _rfpart(x: float) -> float:
    """1 - дробная часть (для интенсивности второго пикселя)."""
    return 1 - _fpart(x)


def wu(x1: int, y1: int, x2: int, y2: int) -> List[PointWithIntensity]:
    """
    Алгоритм Ву (Xiaolin Wu): сглаживание отрезка — на каждом шаге
    зажигаются два пикселя с интенсивностями, пропорциональными расстоянию
    до идеальной линии (сумма интенсивностей = 1).
    """
    points: List[PointWithIntensity] = []
    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        points.append((x1, y1, 1.0))
        return points

    # Горизонтальная / вертикальная / диагональ — без сглаживания
    if abs(dx) == 0 or abs(dy) == 0 or abs(dx) == abs(dy):
        for pt in bresenham(x1, y1, x2, y2):
            points.append((pt[0], pt[1], 1.0))
        return points

    steep = abs(dy) > abs(dx)
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
        dx, dy = dy, dx
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        dx = -dx
        dy = -dy

    grad = dy / dx
    # Первая конечная точка
    x_end = round(x1)
    y_end = y1 + grad * (x_end - x1)
    x_gap = _rfpart(x1 + 0.5)
    px, py = int(x_end), int(math.floor(y_end))
    if steep:
        points.append((py, px, _rfpart(y_end) * x_gap))
        points.append((py + 1, px, _fpart(y_end) * x_gap))
    else:
        points.append((px, py, _rfpart(y_end) * x_gap))
        points.append((px, py + 1, _fpart(y_end) * x_gap))
    intery = y_end + grad
    # Вторая конечная точка
    x_end = round(x2)
    y_end = y2 + grad * (x_end - x2)
    x_gap = _fpart(x2 + 0.5)
    px2, py2 = int(x_end), int(math.floor(y_end))
    if steep:
        points.append((py2, px2, _rfpart(y_end) * x_gap))
        points.append((py2 + 1, px2, _fpart(y_end) * x_gap))
    else:
        points.append((px2, py2, _rfpart(y_end) * x_gap))
        points.append((px2, py2 + 1, _fpart(y_end) * x_gap))
    # Средние точки
    for x in range(int(round(x1)) + 1, int(round(x2))):
        y_floor = math.floor(intery)
        i1 = _rfpart(intery)
        i2 = _fpart(intery)
        if steep:
            points.append((int(y_floor), x, i1))
            points.append((int(y_floor) + 1, x, i2))
        else:
            points.append((x, int(y_floor), i1))
            points.append((x, int(y_floor) + 1, i2))
        intery += grad
    return points


def wu_steps(
    x1: int, y1: int, x2: int, y2: int
) -> Iterator[Tuple[PointWithIntensity, ...]]:
    """Пошаговое выполнение алгоритма Ву для отладки (по два пикселя на шаг по основной оси)."""
    pts = wu(x1, y1, x2, y2)
    i = 0
    while i < len(pts):
        if i + 1 < len(pts):
            yield (pts[i], pts[i + 1])
            i += 2
        else:
            yield (pts[i],)
            i += 1

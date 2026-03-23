from __future__ import annotations

from typing import List, Sequence, Tuple

Point = Tuple[float, float]


def _lerp(a: Point, b: Point, t: float) -> Point:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def hermite_curve(control_points: Sequence[Point], samples: int = 200) -> List[Point]:
    """
    Кубическая кривая Эрмита.
    control_points:
      p0 - начало,
      p1 - конец,
      t0 - точка, задающая направление касательной в p0,
      t1 - точка, задающая направление касательной в p1.
    """
    if len(control_points) != 4:
        return []
    p0, p1, t0, t1 = control_points
    r0 = (t0[0] - p0[0], t0[1] - p0[1])
    r1 = (t1[0] - p1[0], t1[1] - p1[1])
    result: List[Point] = []
    for i in range(samples + 1):
        t = i / samples
        t2 = t * t
        t3 = t2 * t
        h1 = 2 * t3 - 3 * t2 + 1
        h2 = -2 * t3 + 3 * t2
        h3 = t3 - 2 * t2 + t
        h4 = t3 - t2
        x = h1 * p0[0] + h2 * p1[0] + h3 * r0[0] + h4 * r1[0]
        y = h1 * p0[1] + h2 * p1[1] + h3 * r0[1] + h4 * r1[1]
        result.append((x, y))
    return result


def bezier_curve(control_points: Sequence[Point], samples: int = 200) -> List[Point]:
    """Кубическая кривая Безье (4 контрольные точки)."""
    if len(control_points) != 4:
        return []
    p0, p1, p2, p3 = control_points
    result: List[Point] = []
    for i in range(samples + 1):
        t = i / samples
        u = 1 - t
        b0 = u * u * u
        b1 = 3 * t * u * u
        b2 = 3 * t * t * u
        b3 = t * t * t
        x = b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0]
        y = b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1]
        result.append((x, y))
    return result


def bspline_curve(control_points: Sequence[Point], samples_per_segment: int = 70) -> List[Point]:
    """
    Кубический равномерный B-сплайн.
    Для n контрольных точек формируются n-3 сегмента.
    """
    n = len(control_points)
    if n < 4:
        return []

    result: List[Point] = []
    for seg in range(n - 3):
        p0, p1, p2, p3 = control_points[seg : seg + 4]
        for i in range(samples_per_segment + 1):
            t = i / samples_per_segment
            t2 = t * t
            t3 = t2 * t
            b0 = (-t3 + 3 * t2 - 3 * t + 1) / 6.0
            b1 = (3 * t3 - 6 * t2 + 4) / 6.0
            b2 = (-3 * t3 + 3 * t2 + 3 * t + 1) / 6.0
            b3 = t3 / 6.0
            x = b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0]
            y = b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1]
            result.append((x, y))
    return result


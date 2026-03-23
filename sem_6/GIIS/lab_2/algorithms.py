from typing import List, Tuple, Iterator

Point = Tuple[int, int]


# ---------------------------------------------------------------------------
# Окружность: алгоритм Брезенхема (первый квадрант, затем отражения)
# Уравнение: x² + y² = R². Ошибка Δ = x² + y² - R².
# ---------------------------------------------------------------------------


def _circle_octant_points_and_steps(
    r: int,
) -> Tuple[List[Point], List[Tuple[Point, dict]]]:
    """Генерация первого квадранта окружности (от (0,R) по часовой стрелке)."""
    points: List[Point] = []
    steps: List[Tuple[Point, dict]] = []
    if r <= 0:
        return points, steps
    x, y = 0, r
    delta = 1 - 2 * r  # начальная ошибка: (1)² + (r-1)² - r² = 2 - 2r, но в литературе часто 1-2r
    # По пособию: Δ_1 = (0+1)² + (R-1)² - R² = 1 + R² - 2R + 1 - R² = 2 - 2R
    delta = 2 - 2 * r
    while y >= 0 and x <= r:
        points.append((x, y))
        steps.append(((x, y), {"Δ": delta, "δ": None, "δ*": None, "пиксель": "H/V/D"}))
        if delta == 0:
            # Случай В: диагональный шаг
            x += 1
            y -= 1
            delta += 2 * (x - y) + 2
        elif delta < 0:
            # Случай А: H или D. δ = 2*Δ + 2*y - 1 (для выбора между H и D)
            d_val = 2 * delta + 2 * y - 1
            if d_val <= 0:
                # H
                x += 1
                delta += 2 * x + 1
                steps[-1] = ((points[-1]), {"Δ": steps[-1][1]["Δ"], "δ": d_val, "δ*": None, "пиксель": "H"})
            else:
                # D
                x += 1
                y -= 1
                delta += 2 * (x - y) + 2
                steps[-1] = ((points[-1]), {"Δ": steps[-1][1]["Δ"], "δ": d_val, "δ*": None, "пиксель": "D"})
        else:
            # Δ > 0: V или D. δ* = 2*Δ - 2*x - 1
            d_star = 2 * delta - 2 * x - 1
            if d_star <= 0:
                # D
                x += 1
                y -= 1
                delta += 2 * (x - y) + 2
                steps[-1] = ((points[-1]), {"Δ": steps[-1][1]["Δ"], "δ": None, "δ*": d_star, "пиксель": "D"})
            else:
                # V: Δ_{i+1} = Δ + (1 - 2y), затем y -= 1
                delta += 1 - 2 * y
                y -= 1
                steps[-1] = ((points[-1]), {"Δ": steps[-1][1]["Δ"], "δ": None, "δ*": d_star, "пиксель": "V"})
        if y < 0:
            break
    return points, steps


def circle_bresenham(cx: int, cy: int, r: int) -> List[Point]:
    """Окружность с центром (cx, cy) и радиусом r (алгоритм Брезенхема)."""
    if r <= 0:
        return [(cx, cy)] if r == 0 else []
    oct, _ = _circle_octant_points_and_steps(r)
    result: List[Point] = []
    for (x, y) in oct:
        result.append((cx + x, cy + y))
        result.append((cx - x, cy + y))
        result.append((cx + x, cy - y))
        result.append((cx - x, cy - y))
        result.append((cx + y, cy + x))
        result.append((cx - y, cy + x))
        result.append((cx + y, cy - x))
        result.append((cx - y, cy - x))
    return list(dict.fromkeys(result))  # без дубликатов


def circle_steps(cx: int, cy: int, r: int) -> Iterator[Tuple[Point, dict]]:
    """Пошагово: точки первого квадранта с данными для таблицы (отражения применяются при отрисовке)."""
    if r <= 0:
        if r == 0:
            yield ((cx, cy), {"Δ": 0, "δ": None, "δ*": None, "пиксель": "—"})
        return
    _, steps = _circle_octant_points_and_steps(r)
    for ((x, y), extra) in steps:
        yield ((cx + x, cy + y), extra)


def circle_all_steps(cx: int, cy: int, r: int) -> Tuple[List[Point], List[dict]]:
    """Список точек и список доп. данных по шагам (для отладочной таблицы)."""
    points: List[Point] = []
    extras: List[dict] = []
    if r <= 0:
        return points, extras
    oct, step_list = _circle_octant_points_and_steps(r)
    for ((x, y), extra) in step_list:
        points.append((cx + x, cy + y))
        extras.append(extra)
    return points, extras


# ---------------------------------------------------------------------------
# Эллипс: алгоритм Брезенхема (первый квадрант)
# Уравнение: x²/a² + y²/b² = 1  =>  b²x² + a²y² - a²b² = 0. Δ = b²x² + a²y² - a²b².
# ---------------------------------------------------------------------------


def _ellipse_quadrant_points_and_steps(
    a: int, b: int
) -> Tuple[List[Point], List[Tuple[Point, dict]]]:
    """Первый квадрант эллипса от (0, b) по часовой стрелке."""
    points: List[Point] = []
    steps: List[Tuple[Point, dict]] = []
    if a <= 0 or b <= 0:
        return points, steps
    x, y = 0, b
    # Начальная ошибка: (0,b) -> Δ = 0 + a²b² - a²b² = 0; для следующего шага из таблицы 2.2
    # Δ = b²a² - a²b + a²/4  (для точки (0,b) следующая - либо (1,b), либо (1,b-1))
    delta = b * b - a * a * b + (a * a) // 4
    while y >= 0 and x <= a:
        points.append((x, y))
        steps.append(((x, y), {"Δ": delta, "пиксель": "?"}))
        if delta < 0:
            d_val = 2 * delta + b * b * (2 * x + 1)
            if d_val <= 0:
                x += 1
                delta += b * b * (2 * x + 1)
                steps[-1] = ((points[-1]), {"Δ": steps[-1][1]["Δ"], "δ": d_val, "пиксель": "H"})
            else:
                x += 1
                y -= 1
                delta += b * b * (2 * x + 1) + a * a * (1 - 2 * y)
                steps[-1] = ((points[-1]), {"Δ": steps[-1][1]["Δ"], "δ": d_val, "пиксель": "D"})
        elif delta > 0:
            d_star = 2 * delta - a * a * (2 * y - 1)
            if d_star <= 0:
                x += 1
                y -= 1
                delta += b * b * (2 * x + 1) + a * a * (1 - 2 * y)
                steps[-1] = ((points[-1]), {"Δ": steps[-1][1]["Δ"], "δ*": d_star, "пиксель": "D"})
            else:
                y -= 1
                delta += a * a * (1 - 2 * y)
                steps[-1] = ((points[-1]), {"Δ": steps[-1][1]["Δ"], "δ*": d_star, "пиксель": "V"})
        else:
            x += 1
            y -= 1
            delta += b * b * (2 * x + 1) + a * a * (1 - 2 * y)
            steps[-1] = ((points[-1]), {"Δ": steps[-1][1]["Δ"], "пиксель": "D"})
        if y < 0:
            break
    return points, steps


def ellipse(cx: int, cy: int, a: int, b: int) -> List[Point]:
    """Эллипс с центром (cx, cy) и полуосями a, b."""
    if a <= 0 or b <= 0:
        return [(cx, cy)] if a == 0 and b == 0 else []
    quad, _ = _ellipse_quadrant_points_and_steps(a, b)
    result: List[Point] = []
    for (x, y) in quad:
        result.append((cx + x, cy + y))
        result.append((cx - x, cy + y))
        result.append((cx + x, cy - y))
        result.append((cx - x, cy - y))
    return list(dict.fromkeys(result))


def ellipse_all_steps(cx: int, cy: int, a: int, b: int) -> Tuple[List[Point], List[dict]]:
    points, step_list = _ellipse_quadrant_points_and_steps(a, b)
    pts = [(cx + x, cy + y) for (x, y) in points]
    extras = [e for (_, e) in step_list]
    return pts, extras


# ---------------------------------------------------------------------------
# Гипербола: x²/a² - y²/b² = 1, первый квадрант (x ≥ a, y ≥ 0)
# F(x,y) = b²x² - a²y² - a²b². На кривой F=0.
# ---------------------------------------------------------------------------


def hyperbola(cx: int, cy: int, a: int, b: int, x_max: int) -> List[Point]:
    """Ветвь гиперболы в первом квадранте до x ≤ x_max (относительно центра)."""
    if a <= 0 or b <= 0:
        return []
    result: List[Point] = []
    x, y = a, 0
    # F = b²x² - a²y² - a²b²
    f = b * b * x * x - a * a * b * b
    while x <= x_max and x >= 0:
        result.append((cx + x, cy + y))
        result.append((cx + x, cy - y))
        result.append((cx - x, cy + y))
        result.append((cx - x, cy - y))
        # Следующая точка: (x+1, y) или (x+1, y+1). Средняя точка M = (x+1, y+0.5).
        # F = b²x² − a²y² − a²b²: на кривой F=0; ниже ветви (меньше y) F > 0, выше — F < 0.
        # Если F(M) > 0, M ниже кривой → берём верхний пиксель (x+1, y+1).
        f_mid = b * b * (x + 1) * (x + 1) - a * a * (y + 0.5) * (y + 0.5) - a * a * b * b
        if f_mid > 0:
            y += 1
        x += 1
    return result


def hyperbola_steps(cx: int, cy: int, a: int, b: int, x_max: int) -> Tuple[List[Point], List[dict]]:
    points: List[Point] = []
    extras: List[dict] = []
    if a <= 0 or b <= 0:
        return points, extras
    x, y = a, 0
    while x <= x_max and x >= 0:
        f = b * b * x * x - a * a * y * y - a * a * b * b
        points.append((cx + x, cy + y))
        extras.append({"x": x, "y": y, "F": f})
        f_mid = b * b * (x + 1) * (x + 1) - a * a * (y + 0.5) * (y + 0.5) - a * a * b * b
        if f_mid > 0:
            y += 1
        x += 1
    return points, extras


# ---------------------------------------------------------------------------
# Парабола: y² = 2px, первый квадрант (x = y²/(2p))
# ---------------------------------------------------------------------------


def parabola(cx: int, cy: int, p: int, y_max: int) -> List[Point]:
    """Парабола y² = 2px с вершиной в (cx, cy), ветви вправо и влево."""
    if p <= 0:
        return []
    result: List[Point] = []
    for y in range(0, y_max + 1):
        x_val = (y * y) // (2 * p) if p else 0
        x = int(x_val)
        result.append((cx + x, cy + y))
        result.append((cx + x, cy - y))
        if x > 0:
            result.append((cx - x, cy + y))
            result.append((cx - x, cy - y))
    return list(dict.fromkeys(result))


def parabola_steps(cx: int, cy: int, p: int, y_max: int) -> Tuple[List[Point], List[dict]]:
    points: List[Point] = []
    extras: List[dict] = []
    if p <= 0:
        return points, extras
    for y in range(0, y_max + 1):
        x_val = (y * y) / (2 * p)
        x = int(round(x_val))
        points.append((cx + x, cy + y))
        extras.append({"y": y, "x": x, "x_точн": x_val})
    return points, extras

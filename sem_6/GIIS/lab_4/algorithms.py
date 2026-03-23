from __future__ import annotations

from pathlib import Path
from typing import List, Sequence, Tuple

Point3 = Tuple[float, float, float]
Edge = Tuple[int, int]
Vertex4 = Tuple[float, float, float, float]
Matrix4 = List[List[float]]


def identity_matrix() -> Matrix4:
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def matrix_mul(a: Matrix4, b: Matrix4) -> Matrix4:
    res = [[0.0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            s = 0.0
            for k in range(4):
                s += a[i][k] * b[k][j]
            res[i][j] = s
    return res


def apply_matrix_to_vertex(m: Matrix4, v: Vertex4) -> Vertex4:
    out = [0.0, 0.0, 0.0, 0.0]
    for i in range(4):
        out[i] = m[i][0] * v[0] + m[i][1] * v[1] + m[i][2] * v[2] + m[i][3] * v[3]
    return (out[0], out[1], out[2], out[3])


def apply_matrix(vertices: Sequence[Vertex4], m: Matrix4) -> List[Vertex4]:
    return [apply_matrix_to_vertex(m, v) for v in vertices]


def compose(*matrices: Matrix4) -> Matrix4:
    """
    Возвращает композицию для v' = M * v.
    compose(A, B) => B * A (сначала A, потом B).
    """
    result = identity_matrix()
    for m in matrices:
        result = matrix_mul(m, result)
    return result


def translation_matrix(tx: float, ty: float, tz: float) -> Matrix4:
    return [
        [1.0, 0.0, 0.0, tx],
        [0.0, 1.0, 0.0, ty],
        [0.0, 0.0, 1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def scaling_matrix(sx: float, sy: float, sz: float) -> Matrix4:
    return [
        [sx, 0.0, 0.0, 0.0],
        [0.0, sy, 0.0, 0.0],
        [0.0, 0.0, sz, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def rotation_x_matrix(angle_deg: float) -> Matrix4:
    import math

    a = math.radians(angle_deg)
    c = math.cos(a)
    s = math.sin(a)
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c, -s, 0.0],
        [0.0, s, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def rotation_y_matrix(angle_deg: float) -> Matrix4:
    import math

    a = math.radians(angle_deg)
    c = math.cos(a)
    s = math.sin(a)
    return [
        [c, 0.0, s, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s, 0.0, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def rotation_z_matrix(angle_deg: float) -> Matrix4:
    import math

    a = math.radians(angle_deg)
    c = math.cos(a)
    s = math.sin(a)
    return [
        [c, -s, 0.0, 0.0],
        [s, c, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def reflection_matrix(plane: str) -> Matrix4:
    if plane == "OXY":
        return scaling_matrix(1.0, 1.0, -1.0)
    if plane == "OXZ":
        return scaling_matrix(1.0, -1.0, 1.0)
    if plane == "OYZ":
        return scaling_matrix(-1.0, 1.0, 1.0)
    raise ValueError(f"Unknown plane: {plane}")


def vertices_center(vertices: Sequence[Vertex4]) -> Point3:
    if not vertices:
        return (0.0, 0.0, 0.0)
    sx = sy = sz = 0.0
    for x, y, z, w in vertices:
        if w == 0:
            continue
        sx += x / w
        sy += y / w
        sz += z / w
    n = len(vertices)
    return (sx / n, sy / n, sz / n)


def about_point(transform: Matrix4, point: Point3) -> Matrix4:
    px, py, pz = point
    to_origin = translation_matrix(-px, -py, -pz)
    back = translation_matrix(px, py, pz)
    return compose(to_origin, transform, back)


def perspective_matrix(distance: float) -> Matrix4:
    if distance == 0:
        distance = 1.0
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0 / distance, 1.0],
    ]


def project_vertices(vertices: Sequence[Vertex4], use_perspective: bool, distance: float) -> List[Point3]:
    if not use_perspective:
        out: List[Point3] = []
        for x, y, z, w in vertices:
            ww = w if abs(w) > 1e-9 else 1.0
            out.append((x / ww, y / ww, z / ww))
        return out

    p = perspective_matrix(distance)
    projected = apply_matrix(vertices, p)
    out = []
    for x, y, z, w in projected:
        ww = w if abs(w) > 1e-9 else 1.0
        out.append((x / ww, y / ww, z / ww))
    return out


def parse_model(path: str) -> Tuple[List[Vertex4], List[Edge]]:
    """
    Формат файла:
      v x y z
      e i j
    Индексы рёбер 0-based.
    Также поддерживается краткий формат вершины: "x y z".
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(path)

    vertices: List[Vertex4] = []
    edges: List[Edge] = []

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        tag = parts[0].lower()
        if tag == "v":
            if len(parts) < 4:
                continue
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            vertices.append((x, y, z, 1.0))
            continue
        if tag == "e":
            if len(parts) < 3:
                continue
            i, j = int(parts[1]), int(parts[2])
            edges.append((i, j))
            continue

        if len(parts) >= 3:
            try:
                x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
            except ValueError:
                continue
            vertices.append((x, y, z, 1.0))

    if not vertices:
        raise ValueError("В файле не найдено ни одной вершины.")

    if not edges and len(vertices) > 1:
        for i in range(len(vertices) - 1):
            edges.append((i, i + 1))
        if len(vertices) > 2:
            edges.append((len(vertices) - 1, 0))

    return vertices, edges


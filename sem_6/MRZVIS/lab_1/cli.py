"""
CLI для модели арифметического конвейера (вариант 2).
Параметры: n (число стадий), m (длина векторов), ti (время на стадию).

Автор: Семеняко Владиир Дмитриевич
Группа: 321701
"""

import argparse
import random
import sys
from pipeline import (
    P_BITS,
    compute_result_vector,
    get_stage_display_at_tact,
    to_bin_str,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Конвейер попарного умножения 4-разрядных чисел (вариант 2, CLI)."
    )
    parser.add_argument(
        "-n",
        "--stages",
        type=int,
        default=4,
        help="Число стадий конвейера (по умолчанию 4 для p=4)",
    )
    parser.add_argument(
        "-m",
        "--pairs",
        type=int,
        default=8,
        help="Число пар элементов (длина векторов)",
    )
    parser.add_argument(
        "-t",
        "--stage-time",
        type=float,
        default=1.0,
        help="Время одного такта (усл. ед.) для сбалансированного конвейера",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed для генерации векторов (для воспроизводимости)",
    )
    parser.add_argument(
        "--no-animate",
        action="store_true",
        help="Вывести только итог: входные пары, результаты, без пошаговой развёртки",
    )
    parser.add_argument(
        "--mode",
        "-M",
        choices=["generate", "manual"],
        default="generate",
        help="Режим ввода: generate — сгенерировать векторы, manual — ввести вручную",
    )
    parser.add_argument(
        "--vector-a",
        type=str,
        default=None,
        help="В ручном режиме: вектор A через запятую (например 3,0,8,7)",
    )
    parser.add_argument(
        "--vector-b",
        type=str,
        default=None,
        help="В ручном режиме: вектор B через запятую (например 4,3,2,13)",
    )
    return parser.parse_args()


def generate_vectors(m: int, seed: int | None) -> tuple[list[int], list[int]]:
    """Генерация векторов A и B из 4-разрядных чисел (0..15)."""
    rng = random.Random(seed)
    a = [rng.randint(0, 15) for _ in range(m)]
    b = [rng.randint(0, 15) for _ in range(m)]
    return a, b


def parse_vector(s: str) -> list[int]:
    """Парсинг вектора из строки (числа через запятую или пробел)."""
    s = s.replace(",", " ").strip()
    if not s:
        return []
    out = []
    for part in s.split():
        try:
            x = int(part)
        except ValueError:
            raise ValueError(f"Ожидается целое число, получено: {part!r}")
        if not (0 <= x <= 15):
            raise ValueError(f"Число должно быть 4-разрядным (0..15), получено: {x}")
        out.append(x)
    return out


def read_vectors_manual(args) -> tuple[list[int], list[int]]:
    """Ввод векторов в ручном режиме: из аргументов или интерактивно."""
    if args.vector_a is not None and args.vector_b is not None:
        try:
            a = parse_vector(args.vector_a)
            b = parse_vector(args.vector_b)
        except ValueError as e:
            print(f"Ошибка ввода: {e}", file=sys.stderr)
            sys.exit(1)
        if len(a) != len(b):
            print("Ошибка: длины векторов A и B должны совпадать.", file=sys.stderr)
            sys.exit(1)
        if not a:
            print("Ошибка: векторы не могут быть пустыми.", file=sys.stderr)
            sys.exit(1)
        return a, b
    # Интерактивный ввод
    print("Ручной режим: введите векторы (4-разрядные числа 0..15).")
    try:
        raw_a = input("Вектор A (числа через запятую или пробел): ").strip()
        raw_b = input("Вектор B (числа через запятую или пробел): ").strip()
    except EOFError:
        print("Ввод недоступен. Используйте --vector-a и --vector-b.", file=sys.stderr)
        sys.exit(1)
    try:
        a = parse_vector(raw_a)
        b = parse_vector(raw_b)
    except ValueError as e:
        print(f"Ошибка ввода: {e}", file=sys.stderr)
        sys.exit(1)
    if len(a) != len(b):
        print("Ошибка: длины векторов A и B должны совпадать.", file=sys.stderr)
        sys.exit(1)
    if not a:
        print("Ошибка: векторы не могут быть пустыми.", file=sys.stderr)
        sys.exit(1)
    return a, b


def print_section(title: str) -> None:
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_pairs_before_pipeline(vectors_a: list[int], vectors_b: list[int]) -> None:
    """Перед первой стадией: все пары элементов в десятичном виде с номерами."""
    print_section("До первой стадии: пары элементов векторов A и B (десятичный вид)")
    for i in range(len(vectors_a)):
        print(f"  Пара [{i}]:  A[{i}] = {vectors_a[i]},  B[{i}] = {vectors_b[i]}")
    print()


def print_results_after_pipeline(
    vectors_a: list[int],
    vectors_b: list[int],
    results: list[int],
    stage_time: float,
    n_stages: int,
) -> None:
    """После последней стадии: все элементы C с номерами и временем получения."""
    print_section("После последней стадии: элементы результирующего вектора C (десятичный вид)")
    m = len(results)
    for i in range(m):
        tact_out = i + n_stages
        time_out = tact_out * stage_time
        print(f"  C[{i}] = {results[i]}  (пара [{i}], время получения: {time_out} у.е., такт {tact_out})")
    print()


def print_pipeline_state_at_tact(
    tact: int,
    vectors_a: list[int],
    vectors_b: list[int],
    n_stages: int,
    m: int,
    stage_time: float,
    show_input: bool = True,
) -> None:
    """Вывод состояния конвейера в один такт: по стадиям — данные (двоично), индекс пары, время."""
    time_now = tact * stage_time
    print(f"  --- Такт {tact}, время с старта: {time_now} у.е. ---")
    for stage in range(1, n_stages + 1):
        info = get_stage_display_at_tact(vectors_a, vectors_b, tact, stage, n_stages, m)
        if info is None:
            continue
        idx = info["pair_index"]
        # По требованию: на стадии выводить либо входные, либо выходные данные
        val = info["input_partial"] if show_input else info["output_partial"]
        bin_str = to_bin_str(val, 8, " ")
        print(f"    Стадия {stage}:  индекс пары [{idx}],  данные (двоично): {bin_str}")
    print()


def run_interactive_steps(
    vectors_a: list[int],
    vectors_b: list[int],
    n_stages: int,
    stage_time: float,
) -> None:
    """Пошаговый вывод по тактам (визуализация процесса)."""
    m = len(vectors_a)
    total_tacts = m + n_stages - 1
    print_section("Пошаговая работа конвейера (данные на стадиях — вход)")
    for tact in range(1, total_tacts + 1):
        print_pipeline_state_at_tact(
            tact, vectors_a, vectors_b, n_stages, m, stage_time, show_input=True
        )


def main() -> int:
    args = parse_args()
    n, ti = args.stages, args.stage_time
    if n != P_BITS:
        print(f"Для варианта 2 число стадий должно быть {P_BITS} (4-разрядное умножение).", file=sys.stderr)
        n = P_BITS

    if args.mode == "manual":
        vectors_a, vectors_b = read_vectors_manual(args)
    else:
        m = args.pairs
        vectors_a, vectors_b = generate_vectors(m, args.seed)
    m = len(vectors_a)
    stage_times = [ti] * n

    print("Параметры: n = {}, m = {}, ti = {} у.е., режим = {}.".format(n, m, ti, args.mode))
    if args.mode == "generate":
        print("Векторы сгенерированы (4-разрядные числа 0..15).")
    else:
        print("Векторы заданы вручную.")

    print_pairs_before_pipeline(vectors_a, vectors_b)

    if not args.no_animate:
        run_interactive_steps(vectors_a, vectors_b, n, ti)

    results = compute_result_vector(vectors_a, vectors_b)
    print_results_after_pipeline(vectors_a, vectors_b, results, ti, n)

    print_section("Краткая сводка")
    print("  Вектор A:", vectors_a)
    print("  Вектор B:", vectors_b)
    print("  Вектор C (A*B):", results)
    return 0


if __name__ == "__main__":
    sys.exit(main())

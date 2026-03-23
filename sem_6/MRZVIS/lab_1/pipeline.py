"""
Модель арифметического конвейера для попарного умножения компонентов двух векторов.
Вариант 2: умножение 4-разрядных чисел с младших разрядов со сдвигом частичной суммы вправо.

Автор: Семеняко Владиир Дмитриевич
Группа: 321701
"""

P_BITS = 4  # разрядность чисел по варианту 2


def to_bin_str(value: int, bits: int, group_sep: str = " ") -> str:
    """Форматирование числа в двоичный вид группами по 4 символа."""
    s = bin(value)[2:].zfill(bits)
    return group_sep.join(s[i : i + 4] for i in range(0, len(s), 4))


def mul_4bit_lsb_right_shift(a: int, b: int) -> int:
    """
    Произведение пары 4-разрядных чисел: умножение с младших разрядов
    со сдвигом частичной суммы вправо.
    На каждом шаге: прибавить множимое в старшую половину (a<<4), если разряд множителя 1; сдвиг вправо.
    Возвращает 8-разрядный результат (2p).
    """
    p = 0
    for i in range(P_BITS):
        if (b >> i) & 1:
            p += a << P_BITS  # множимое в старшую половину 8-битного регистра
        p >>= 1
    return p & 0xFF


def pipeline_stage_step(partial: int, a: int, b: int, bit_index: int) -> int:
    """
    Один шаг конвейера: обработка одного разряда множителя (LSB-first, сдвиг частичной суммы вправо).
    partial — текущая частичная сумма (8 бит), a — множимое, b — множитель, bit_index — номер разряда (0..3).
    """
    if (b >> bit_index) & 1:
        partial += a << P_BITS
    partial >>= 1
    return partial & 0xFF


def run_pipeline_cycle(
    vectors_a: list[int],
    vectors_b: list[int],
    n_stages: int,
    stage_times: list[float],
) -> list[tuple]:
    """
    Симуляция конвейера по тактам.
    Возвращает список событий (tact, stage, pair_index, partial_bin, time_accum).
    """
    m = len(vectors_a)
    assert len(vectors_b) == m
    assert n_stages == P_BITS and len(stage_times) == n_stages

    events = []
    # Состояние конвейера: для каждой стадии (pair_index, partial, bit_index) или None
    # stage_data[0] — после входа, stage_data[i] — после стадии i (i=1..n)
    # В такт t: в стадию 1 входит пара t; в стадию 2 — пара t-1 и т.д.
    total_tacts = m + n_stages - 1
    time_per_stage = stage_times[0]  # сбалансированный — все ti равны

    for tact in range(1, total_tacts + 1):
        for stage in range(1, n_stages + 1):
            pair_idx = tact - stage
            if pair_idx < 0 or pair_idx >= m:
                continue
            a, b = vectors_a[pair_idx], vectors_b[pair_idx]
            if stage == 1:
                partial = 0
            else:
                prev_partial = 0
                for prev_bit in range(stage - 1):
                    prev_partial = pipeline_stage_step(prev_partial, a, b, prev_bit)
                partial = prev_partial
            partial = pipeline_stage_step(partial, a, b, stage - 1)
            time_accum = tact * time_per_stage
            events.append((tact, stage, pair_idx, partial, time_accum))
    return events


def compute_result_vector(vectors_a: list[int], vectors_b: list[int]) -> list[int]:
    """Вычисление результирующего вектора C (попарные произведения)."""
    return [
        mul_4bit_lsb_right_shift(a, b) for a, b in zip(vectors_a, vectors_b)
    ]


def get_stage_display_at_tact(
    vectors_a: list[int],
    vectors_b: list[int],
    tact: int,
    stage: int,
    n_stages: int,
    m: int,
) -> dict | None:
    """
    Для такта tact и стадии stage возвращает данные для отображения:
    pair_index, input_partial (вход на стадию), output_partial (выход), time.
    """
    # В такт tact в стадии stage обрабатывается пара, вошедшая в конвейер (tact - stage) тактов назад
    pair_idx = tact - stage
    if pair_idx < 0 or pair_idx >= m:
        return None
    a, b = vectors_a[pair_idx], vectors_b[pair_idx]
    # Входное значение частичной суммы на эту стадию
    input_partial = 0
    for i in range(stage - 1):
        input_partial = pipeline_stage_step(input_partial, a, b, i)
    output_partial = pipeline_stage_step(input_partial, a, b, stage - 1)
    return {
        "pair_index": pair_idx,
        "a": a,
        "b": b,
        "input_partial": input_partial,
        "output_partial": output_partial,
        "stage": stage,
    }

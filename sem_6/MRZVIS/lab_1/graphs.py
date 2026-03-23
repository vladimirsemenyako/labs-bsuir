# -*- coding: utf-8 -*-
"""
Расчёт данных и построение графиков ускорения и эффективности конвейера для отчёта.
Запуск: python3 graphs.py
Создаёт: report_data_family1.csv, report_data_family2.csv, рис_1_1_Ку_от_г.png, рис_1_2_Э_от_г.png, рис_2_1_Ку_от_n.png, рис_2_2_Э_от_n.png

Автор: [ФИО]
Группа: [номер]
"""

import csv
import os

# Формулы конвейера (сбалансированный, ti = 1 у.е.):
# T_seq = m * n * ti  — время последовательного выполнения для m пар при n стадиях
# T_pipeline = (m + n - 1) * ti  — время конвейера до получения всех m результатов
# Ускорение S = T_seq / T_pipeline = (m * n) / (m + n - 1)
# Эффективность E = S / n = m / (m + n - 1)


def pipeline_time_sequential(m: int, n: int, ti: float = 1.0) -> float:
    """Время последовательного выполнения (без конвейера)."""
    return m * n * ti


def pipeline_time_parallel(m: int, n: int, ti: float = 1.0) -> float:
    """Время работы конвейера до выхода всех m результатов."""
    return (m + n - 1) * ti


def speedup(m: int, n: int) -> float:
    """Ускорение S = T_seq / T_pipeline."""
    return (m * n) / (m + n - 1)


def efficiency(m: int, n: int) -> float:
    """Эффективность E = S / n."""
    return m / (m + n - 1)


def build_family1(ti: float = 1.0, n_fixed: int = 4):
    """
    Семейство 1: фиксируем n (число стадий), меняем m (число пар).
    Данные для графиков S(m) и E(m).
    """
    m_values = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 75, 100]
    rows = []
    for m in m_values:
        t_seq = pipeline_time_sequential(m, n_fixed, ti)
        t_pipe = pipeline_time_parallel(m, n_fixed, ti)
        s = speedup(m, n_fixed)
        e = efficiency(m, n_fixed)
        rows.append({"m": m, "n": n_fixed, "T_seq": t_seq, "T_pipeline": t_pipe, "S": s, "E": e})
    return rows


def build_family2(ti: float = 1.0, m_fixed: int = 20):
    """
    Семейство 2: фиксируем m (число пар), меняем n (число стадий).
    Теоретические кривые для разного числа стадий (для отчёта).
    """
    n_values = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30]
    rows = []
    for n in n_values:
        t_seq = pipeline_time_sequential(m_fixed, n, ti)
        t_pipe = pipeline_time_parallel(m_fixed, n, ti)
        s = speedup(m_fixed, n)
        e = efficiency(m_fixed, n)
        rows.append({"m": m_fixed, "n": n, "T_seq": t_seq, "T_pipeline": t_pipe, "S": s, "E": e})
    return rows


def save_csv(path: str, rows: list, fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ti = 1.0
    n_fixed = 4
    m_fixed = 20

    # Семейство 1: n=4, m переменная
    family1 = build_family1(ti, n_fixed)
    path1 = os.path.join(script_dir, "report_data_family1.csv")
    save_csv(path1, family1, ["m", "n", "T_seq", "T_pipeline", "S", "E"])
    print("Сохранено:", path1)

    # Семейство 2: m=20, n переменная
    family2 = build_family2(ti, m_fixed)
    path2 = os.path.join(script_dir, "report_data_family2.csv")
    save_csv(path2, family2, ["m", "n", "T_seq", "T_pipeline", "S", "E"])
    print("Сохранено:", path2)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib не установлен. Установите: pip install matplotlib")
        return

    # Ранг задачи r = m (число пар). Для графика как в образце: r 1..20, серии n=1, n=6, асимптота.
    r_vals = list(range(1, 21))
    asymptote_n = 6

    # Рис 1.1 — зависимость коэффициента ускорения Ку от ранга задачи г (серии n=1, n=6, асимптота)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(r_vals, [1.0] * len(r_vals), c="red", s=25, zorder=2, label="n=1")
    ax.scatter(r_vals, [speedup(r, asymptote_n) for r in r_vals], c="blue", s=25, zorder=2, label="n=6")
    ax.scatter(r_vals, [asymptote_n] * len(r_vals), c="gold", s=25, zorder=2, label="асимптота")
    ax.set_xlabel("Ранг задачи, r")
    ax.set_ylabel("Коэффициент ускорения, Ку")
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 8)
    ax.grid(True, alpha=0.3)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_yticks([0, 2, 4, 6, 8])
    ax.legend(loc="lower right")
    plt.tight_layout()
    p1 = os.path.join(script_dir, "рис_1_1_Ку_от_г.png")
    plt.savefig(p1, dpi=150, bbox_inches="tight")
    plt.close()
    print("Сохранён:", p1)

    # Рис 1.2 — зависимость эффективности Э от ранга г (n=1, n=4, n=6)
    fig, ax = plt.subplots(figsize=(6, 4))
    for n_val, color, lbl in [(1, "red", "n=1"), (4, "blue", "n=4"), (6, "green", "n=6")]:
        ax.scatter(r_vals, [efficiency(r, n_val) for r in r_vals], c=color, s=25, zorder=2, label=lbl)
    ax.set_xlabel("Ранг задачи, r")
    ax.set_ylabel("Коэффициент эффективности, e")
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    plt.tight_layout()
    p2 = os.path.join(script_dir, "рис_1_2_Э_от_г.png")
    plt.savefig(p2, dpi=150, bbox_inches="tight")
    plt.close()
    print("Сохранён:", p2)

    # Рис 2.1 — зависимость Ку от n (фиксирован r=20)
    n_list = [r["n"] for r in family2]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(n_list, [r["S"] for r in family2], c="blue", s=25, zorder=2, label="r=20")
    ax.set_xlabel("Число стадий, n")
    ax.set_ylabel("Коэффициент ускорения, Ку")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left")
    plt.tight_layout()
    p3 = os.path.join(script_dir, "рис_2_1_Ку_от_n.png")
    plt.savefig(p3, dpi=150, bbox_inches="tight")
    plt.close()
    print("Сохранён:", p3)

    # Рис 2.2 — зависимость Э от n (фиксирован r=20)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(n_list, [r["E"] for r in family2], c="green", s=25, zorder=2, label="r=20")
    ax.set_xlabel("Число стадий, n")
    ax.set_ylabel("Коэффициент эффективности, e")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left")
    plt.tight_layout()
    p4 = os.path.join(script_dir, "рис_2_2_Э_от_n.png")
    plt.savefig(p4, dpi=150, bbox_inches="tight")
    plt.close()
    print("Сохранён:", p4)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Normalize raw Excel datasets into clean CSV files for the FastAPI backend.

The raw files in data_xlsx/ have inconsistent headers, merged cells and
additional annotations.  This script parses each workbook explicitly and
exports a tabular representation with the following guarantees:
    - Columns "indicator" and "entity" are always present.
    - Year columns are numeric (1990-2035) and sorted ascending.
    - Missing numeric values are left blank.

Usage:
    python scripts/normalize_datasets.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data_xlsx"
OUT_DIR = PROJECT_ROOT / "data_clean"


# --------------------------------------------------------------------------------------
# Utilities
# --------------------------------------------------------------------------------------

def normalize_text(value) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def try_parse_year(value) -> int | None:
    text = normalize_text(value)
    if not text:
        return None
    text = text.replace(".0", "")
    if not text.isdigit():
        return None
    year = int(text)
    if 1900 <= year <= 2035:
        return year
    return None


def clean_numeric(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value):
            return None
        return float(value)
    text = (
        str(value)
        .replace("\u202f", "")
        .replace(" ", "")
        .replace("%", "")
        .replace('"', "")
        .replace("'", "")
        .replace("<", "")
        .replace(">", "")
    )
    if not text or text in {"…", "...", "-", "nan", "None"}:
        return None
    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def find_year_columns(df: pd.DataFrame) -> Tuple[int, List[Tuple[int, int]]]:
    """
    Returns (header_row_index, [(column_index, year), ...])
    """
    for idx in range(len(df)):
        row = df.iloc[idx]
        years: List[Tuple[int, int]] = []
        for col_idx, value in enumerate(row):
            year = try_parse_year(value)
            if year is not None:
                years.append((col_idx, year))
        if len(years) >= 3:
            return idx, years
    raise ValueError("Could not detect header row with year columns")


def ensure_column_order(df: pd.DataFrame) -> pd.DataFrame:
    base_cols = [col for col in df.columns if not str(col).isdigit()]
    year_cols = sorted(
        [col for col in df.columns if str(col).isdigit()], key=lambda c: int(c)
    )
    ordered = base_cols + year_cols
    return df.reindex(columns=ordered)


def filter_indicator(text: str) -> bool:
    lowered = text.lower()
    skip_tokens = [
        "таблица",
        "временные ряды",
        "единица",
        "справочно",
        "примечание",
        "по данным",
        "название реки",
    ]
    return not any(token in lowered for token in skip_tokens)


def is_numeric_code(text: str) -> bool:
    if not text:
        return False
    cleaned = text.replace(".", "").replace(",", "")
    return cleaned.isdigit()


# --------------------------------------------------------------------------------------
# Dataset-specific parsers
# --------------------------------------------------------------------------------------

def parse_simple(
    df: pd.DataFrame, *, default_entity: str = "Беларусь"
) -> pd.DataFrame:
    header_idx, year_cols = find_year_columns(df)
    rows: List[Dict[str, float]] = []

    for idx in range(header_idx + 1, len(df)):
        row = df.iloc[idx]
        indicator = normalize_text(row.iloc[1] if len(row) > 1 else "")
        if not indicator:
            indicator = normalize_text(row.iloc[0])
        if not indicator or not filter_indicator(indicator):
            continue

        values: Dict[str, float] = {}
        for col_idx, year in year_cols:
            if col_idx >= len(row):
                continue
            value = clean_numeric(row.iloc[col_idx])
            if value is not None:
                values[str(year)] = value

        if not values:
            continue

        data_row = {"indicator": indicator, "entity": default_entity}
        data_row.update(values)
        rows.append(data_row)

    if not rows:
        raise ValueError("No data rows parsed for simple dataset")

    return ensure_column_order(pd.DataFrame(rows))


def parse_c9(df: pd.DataFrame) -> pd.DataFrame:
    header_idx, year_cols = find_year_columns(df)
    rows: List[Dict[str, float]] = []
    current_group = ""
    current_subgroup = ""

    for idx in range(header_idx + 1, len(df)):
        row = df.iloc[idx]
        first = normalize_text(row.iloc[0] if len(row) > 0 else "")
        second = normalize_text(row.iloc[1] if len(row) > 1 else "")

        if not first and second:
            if "подземные" in second.lower() or "коммунальные" in second.lower():
                current_group = second
                current_subgroup = ""
                continue
            if "по " in second.lower():
                current_subgroup = second
                continue

        if not is_numeric_code(first):
            continue

        full_indicator = " - ".join(
            part for part in (current_group, current_subgroup, second) if part
        )
        if not full_indicator:
            continue

        values: Dict[str, float] = {}
        for col_idx, year in year_cols:
            if col_idx >= len(row):
                continue
            value = clean_numeric(row.iloc[col_idx])
            if value is not None:
                values[str(year)] = value

        if not values:
            continue

        record = {"indicator": full_indicator, "entity": "Беларусь"}
        record.update(values)
        rows.append(record)

    if not rows:
        raise ValueError("Failed to parse C9 dataset")

    return ensure_column_order(pd.DataFrame(rows))


def parse_c10(df: pd.DataFrame) -> pd.DataFrame:
    header_idx, year_cols = find_year_columns(df)
    rows: List[Dict[str, float]] = []
    current_river = "Неизвестная река"

    # Попробуем найти название реки в любом месте таблицы
    for idx in range(len(df)):
        text_values = [normalize_text(val) for val in df.iloc[idx].tolist()]
        if any("название реки" in text.lower() for text in text_values if text):
            for text in text_values:
                if text and "название реки" not in text.lower():
                    current_river = text
                    break
            break

    for idx in range(header_idx + 1, len(df)):
        row = df.iloc[idx]

        first = normalize_text(row.iloc[0] if len(row) > 0 else "")
        indicator = normalize_text(row.iloc[1] if len(row) > 1 else "")
        if not is_numeric_code(first) or not indicator:
            continue

        values: Dict[str, float] = {}
        for col_idx, year in year_cols:
            if col_idx >= len(row):
                continue
            value = clean_numeric(row.iloc[col_idx])
            if value is not None:
                values[str(year)] = value

        if not values:
            continue

        record = {"indicator": indicator, "entity": current_river}
        record.update(values)
        rows.append(record)

    if not rows:
        raise ValueError("Failed to parse C10 dataset")

    return ensure_column_order(pd.DataFrame(rows))


def _categorize_c11_sheet(sheet_name: str) -> str | None:
    lower = sheet_name.lower()
    if "реки" in lower:
        return "Реки"
    if "озера" in lower:
        return "Озера"
    if "подземные воды" in lower:
        return "Подземные воды"
    return None


def _parse_c11_surface_sheet(df: pd.DataFrame, category: str) -> pd.DataFrame:
    _, year_cols = find_year_columns(df)
    rows: List[Dict[str, float]] = []
    current_indicator = ""

    for idx in range(len(df)):
        row = df.iloc[idx]
        texts = [normalize_text(val) for val in row.tolist() if normalize_text(val)]
        if not texts:
            continue

        if any("единица" in txt.lower() for txt in texts):
            continue

        if len(texts) == 1 and "(" in texts[0]:
            current_indicator = texts[0]
            continue

        first = normalize_text(row.iloc[0] if len(row) > 0 else "")
        if not is_numeric_code(first):
            continue

        entity_name = normalize_text(row.iloc[1] if len(row) > 1 else "")
        if not entity_name:
            continue

        values: Dict[str, float] = {}
        for col_idx, year in year_cols:
            if col_idx >= len(row):
                continue
            value = clean_numeric(row.iloc[col_idx])
            if value is not None:
                values[str(year)] = value

        if not values:
            continue

        record = {
            "indicator": current_indicator or "Показатель",
            "entity": entity_name,
            "category": category,
        }
        record.update(values)
        rows.append(record)

    return pd.DataFrame(rows)


def _parse_c11_groundwater_sheet(df: pd.DataFrame, year: int) -> List[Tuple[str, float]]:
    value_col = None
    start_idx = 0
    for i in range(len(df)):
        for j, val in enumerate(df.iloc[i]):
            if isinstance(val, str) and "фактическое значение" in val.lower():
                value_col = j
                start_idx = i + 1
                break
        if value_col is not None:
            break

    if value_col is None:
        return []

    current_basin = None
    measurements: List[Tuple[str, float]] = []
    for idx in range(start_idx, len(df)):
        texts = [normalize_text(val) for val in df.iloc[idx].tolist() if normalize_text(val)]
        if any("бассейн реки" in text.lower() for text in texts):
            basin_text = next(
                (text for text in texts if "бассейн реки" in text.lower()),
                ""
            )
            basin_name = basin_text.split("Бассейн реки")[-1].strip()
            basin_name = basin_name.replace(":", "").strip()
            current_basin = basin_name or current_basin
            continue

        first = normalize_text(df.iloc[idx, 0] if len(df.columns) > 0 else "")
        if not is_numeric_code(first):
            continue
        if not current_basin:
            continue

        value = clean_numeric(df.iloc[idx, value_col])
        if value is None:
            continue

        measurements.append((current_basin, value))

    return measurements


def parse_c11_workbook(path: Path) -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    frames: List[pd.DataFrame] = []

    # Surface waters (rivers, lakes)
    for sheet in xl.sheet_names:
        category = _categorize_c11_sheet(sheet)
        if category not in {"Реки", "Озера"}:
            continue
        df_sheet = xl.parse(sheet, header=None)
        parsed = _parse_c11_surface_sheet(df_sheet, category)
        if not parsed.empty:
            frames.append(parsed)

    # Groundwater sheets need to be combined across multiple years
    groundwater_stats: Dict[str, Dict[str, List[float]]] = {}
    for sheet in xl.sheet_names:
        category = _categorize_c11_sheet(sheet)
        if category != "Подземные воды":
            continue
        df_sheet = xl.parse(sheet, header=None)
        if "2005-2015" in sheet:
            year = 2015
        else:
            digits = "".join(ch for ch in sheet if ch.isdigit())
            year = int(digits[-4:]) if digits[-4:] else 0
        if year == 0:
            continue
        measurements = _parse_c11_groundwater_sheet(df_sheet, year)
        for basin, value in measurements:
            basin_map = groundwater_stats.setdefault(basin, {})
            basin_map.setdefault(str(year), []).append(value)

    if groundwater_stats:
        gw_rows = []
        for basin, year_values in groundwater_stats.items():
            record = {
                "indicator": "Нитраты (NO3)",
                "entity": basin,
                "category": "Подземные воды",
            }
            for year_str, values in year_values.items():
                record[year_str] = fmean(values)
            gw_rows.append(record)
        frames.append(pd.DataFrame(gw_rows))

    if not frames:
        raise ValueError("Failed to parse C11 workbook")

    combined = pd.concat(frames, ignore_index=True, sort=False)
    combined = combined.fillna("")
    return ensure_column_order(combined)


def parse_c16(df: pd.DataFrame) -> pd.DataFrame:
    # Several textual tags are present; treat as simple table.
    return parse_simple(df, default_entity="Беларусь")


# --------------------------------------------------------------------------------------
# Dataset registry
# --------------------------------------------------------------------------------------

@dataclass
class DatasetSpec:
    name: str
    source: str
    parser: Callable
    use_workbook: bool = False


SIMPLE_DATASETS = [
    "C1-1990-2023",
    "C2-1990-2024",
    "C3-1990-2024",
    "C4-2001-2024",
    "C5-2001-2024",
    "C6-2005-2025",
    "C7-1990-2024",
    "С14-2005-2025",
]

DATASETS: List[DatasetSpec] = [
    DatasetSpec(name=name, source=f"{name}.xlsx", parser=parse_simple)
    for name in SIMPLE_DATASETS
] + [
    DatasetSpec(name="C9-2016-2024", source="C9-2016-2024.xlsx", parser=parse_c9),
    DatasetSpec(name="C10-2005-2024", source="C10-2005-2024.xlsx", parser=parse_c10),
    DatasetSpec(
        name="C11-2005-2024",
        source="C11-2005-2024.xlsx",
        parser=parse_c11_workbook,
        use_workbook=True,
    ),
    DatasetSpec(
        name="C16-2005-2024 01.39.16",
        source="C16-2005-2024 01.39.16.xlsx",
        parser=parse_c16,
    ),
]


# --------------------------------------------------------------------------------------
# Main workflow
# --------------------------------------------------------------------------------------

def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    summary: List[Tuple[str, int]] = []

    for spec in DATASETS:
        source_path = RAW_DIR / spec.source
        if not source_path.exists():
            raise FileNotFoundError(f"Missing source file: {source_path}")

        if spec.use_workbook:
            clean_df = spec.parser(source_path)
        else:
            df_raw = pd.read_excel(source_path, header=None)
            clean_df = spec.parser(df_raw)

        clean_df = clean_df.fillna("")

        output_path = OUT_DIR / f"{spec.name}.csv"
        clean_df.to_csv(output_path, index=False)
        summary.append((spec.name, len(clean_df)))

    print("Saved clean datasets:")
    for name, rows in summary:
        print(f"  - {name}.csv ({rows} rows)")


if __name__ == "__main__":
    main()


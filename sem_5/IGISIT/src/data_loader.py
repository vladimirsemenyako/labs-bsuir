import logging
import math
import os
from typing import Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

KNOWN_RIVERS = [
    'Березина',
    'Вилия',
    'Днепр',
    'Западная Двина',
    'Западный Буг',
    'Мухавец',
    'Неман',
    'Припять',
    'Свислочь',
    'Сож',
]


class DataLoader:
    """
    Lightweight loader that works with the normalized CSV files from data_clean/.
    Each file must contain the columns:
        - indicator: str
        - entity: str (automatically added as 'Беларусь' when missing)
        - <year>: numeric columns for every available year
    """

    def __init__(self, data_dir: str = 'data_clean'):
        self.data_dir = data_dir
        self.cache: Dict[str, pd.DataFrame] = {}

    def _resolve_path(self, filename: str) -> str:
        return os.path.join(self.data_dir, filename)

    def load_csv(self, filename: str) -> pd.DataFrame:
        if filename in self.cache:
            return self.cache[filename]

        path = self._resolve_path(filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dataset not found: {path}")

        df = pd.read_csv(path)
        df.columns = [str(col).strip() for col in df.columns]

        if 'indicator' not in df.columns:
            raise ValueError(
                f"Dataset {filename} must contain an 'indicator' column. "
                "Re-run scripts/normalize_datasets.py."
            )

        if 'entity' not in df.columns:
            df['entity'] = 'Беларусь'

        self.cache[filename] = df
        return df

    def _year_columns(self, df: pd.DataFrame) -> List[str]:
        return sorted([col for col in df.columns if col.isdigit()], key=int)

    def detect_structure(
        self, df: pd.DataFrame
    ) -> Tuple[bool, List[str], str, List[str], List[str]]:
        if df.empty:
            return False, [], 'unknown', []

        indicators = sorted(
            df['indicator'].dropna().astype(str).unique().tolist()
        )

        has_entities = 'entity' in df.columns and df['entity'].nunique() > 1
        entities = (
            sorted(df['entity'].dropna().astype(str).unique().tolist())
            if has_entities
            else []
        )

        categories = (
            sorted(df['category'].dropna().astype(str).unique().tolist())
            if 'category' in df.columns
            else []
        )

        entity_type = 'belarus'
        if has_entities:
            if any(entity in KNOWN_RIVERS for entity in entities):
                entity_type = 'river'
            else:
                entity_type = 'region'

        return has_entities, entities, entity_type, indicators, categories

    def get_all_rows_with_data(self, df: pd.DataFrame) -> List[Dict]:
        """
        Debug helper used by /api/debug to quickly inspect parsed datasets.
        """
        year_cols = self._year_columns(df)
        rows = []
        for _, row in df.iterrows():
            non_empty = sum(
                1
                for col in year_cols
                if pd.notna(row.get(col)) and row.get(col) not in {'', None}
            )
            if non_empty:
                rows.append(
                    {
                        "indicator": row['indicator'],
                        "entity": row.get('entity', 'Беларусь'),
                        "values": non_empty,
                    }
                )
        return rows

    def prepare_timeseries(
        self,
        df: pd.DataFrame,
        indicator: Optional[str] = None,
        entity: Optional[str] = None,
        category: Optional[str] = None,
    ) -> pd.DataFrame:
        subset = df.copy()

        if indicator and indicator not in {'', 'Автоматически'}:
            subset = subset[subset['indicator'] == indicator]

        if category and 'category' in subset.columns:
            subset = subset[subset['category'] == category]

        if entity and entity not in {'', 'Все'} and 'entity' in subset.columns:
            subset = subset[subset['entity'] == entity]

        if subset.empty:
            subset = df.iloc[[0]]

        row = subset.iloc[0]
        year_cols = self._year_columns(df)

        years: List[int] = []
        values: List[float] = []
        for col in year_cols:
            value = row.get(col)
            if value in {'', None} or pd.isna(value):
                continue
            try:
                value_float = float(value)
            except (ValueError, TypeError):
                continue
            years.append(int(col))
            values.append(value_float)

        if not years:
            return pd.DataFrame()

        return pd.DataFrame(
            {
                'year': pd.to_datetime(years, format='%Y'),
                'value': values,
            }
        ).sort_values('year')

    def get_entity_data(
        self,
        df: pd.DataFrame,
        year: int,
        entities: List[str],
        indicator: Optional[str] = None,
        category: Optional[str] = None,
        fallback_to_nearest: bool = True,
    ) -> Tuple[Dict[str, float], int]:
        if 'entity' not in df.columns:
            return {}, year

        subset = df.copy()
        if indicator and indicator not in {'', 'Автоматически'}:
            subset = subset[subset['indicator'] == indicator]

        if category and 'category' in subset.columns:
            subset = subset[subset['category'] == category]

        year_columns = self._year_columns(df)
        if not year_columns:
            return {}, year

        available_years = sorted(int(col) for col in year_columns)

        entity_names = (
            entities
            if entities
            else subset['entity'].dropna().astype(str).unique().tolist()
        )

        if not entity_names:
            return {}, year

        def collect_values(target_year: int) -> Dict[str, float]:
            year_col = str(target_year)
            if year_col not in subset.columns:
                return {}

            values: Dict[str, float] = {}
            for entity in entity_names:
                rows = subset[subset['entity'] == entity]
                if rows.empty:
                    continue
                value_float = None
                for _, row in rows.iterrows():
                    value = row.get(year_col)
                    if value in {'', None} or (isinstance(value, str) and not value.strip()):
                        continue
                    try:
                        candidate = float(value)
                    except (TypeError, ValueError):
                        continue
                    if math.isnan(candidate) or math.isinf(candidate):
                        continue
                    value_float = candidate
                    break
                if value_float is None:
                    continue
                values[entity] = value_float
            return values

        search_order: List[int] = []
        if year in available_years:
            search_order.append(year)

        if fallback_to_nearest:
            earlier = sorted((y for y in available_years if y < year), reverse=True)
            later = sorted(y for y in available_years if y > year)
            for candidate in earlier + later:
                if candidate not in search_order:
                    search_order.append(candidate)
        else:
            if year not in search_order:
                search_order.append(year)

        for candidate_year in search_order:
            values = collect_values(candidate_year)
            if values:
                return values, candidate_year

        return {}, year

    def get_year_range(self, df: pd.DataFrame) -> Tuple[int, int]:
        year_cols = self._year_columns(df)
        if not year_cols:
            return 2000, 2024
        years = [int(col) for col in year_cols]
        return min(years), max(years)


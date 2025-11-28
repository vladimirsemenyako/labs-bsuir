import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.kernel_ridge import KernelRidge

try:
    from sklearn.preprocessing import SplineTransformer  # type: ignore
except ImportError:  # pragma: no cover
    SplineTransformer = None
from sklearn.metrics import mean_squared_error
from typing import Tuple
import warnings

warnings.filterwarnings('ignore')


class TimeSeriesForecaster:
    def __init__(self):
        self.model = None
        self.method = None

    def forecast_prophet(self, df: pd.DataFrame, periods: int = 10) -> pd.DataFrame:
        df_prophet = df.copy()

        if 'year' not in df_prophet.columns or 'value' not in df_prophet.columns:
            raise ValueError("DataFrame must have 'year' and 'value' columns")

        df_prophet = df_prophet[['year', 'value']].copy()
        df_prophet.columns = ['ds', 'y']

        if df_prophet['y'].isna().all():
            raise ValueError("All values are NaN")

        df_prophet = df_prophet.dropna()

        if len(df_prophet) < 3:
            raise ValueError("Not enough data for Prophet")

        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
        )
        model.fit(df_prophet)

        future = model.make_future_dataframe(periods=periods, freq='Y')
        forecast = model.predict(future)

        result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        result.columns = ['year', 'forecast', 'lower', 'upper']

        return result

    def _prepare_year_numeric(self, df_clean: pd.DataFrame) -> pd.Series:
        year_series = df_clean['year']
        if np.issubdtype(year_series.dtype, np.datetime64):
            return year_series.dt.year
        if np.issubdtype(year_series.dtype, np.number):
            return year_series.astype(int)

        parsed = pd.to_datetime(year_series, format='%Y', errors='coerce').dt.year
        null_mask = parsed.isna()
        if null_mask.any():
            parsed.loc[null_mask] = pd.to_datetime(year_series[null_mask], errors='coerce').dt.year
        return parsed

    def forecast_polynomial(
        self, df: pd.DataFrame, periods: int = 10, max_degree: int = 5
    ) -> Tuple[pd.DataFrame, str]:
        df_clean = df.copy()

        if 'year' not in df_clean.columns or 'value' not in df_clean.columns:
            raise ValueError("DataFrame must have 'year' and 'value' columns")

        df_clean['year_numeric'] = self._prepare_year_numeric(df_clean)
        df_clean = df_clean.dropna(subset=['year_numeric', 'value'])

        if df_clean.empty:
            raise ValueError("Нет корректных значений года для полиномиальной регрессии")

        year_values = df_clean['year_numeric'].astype(float).values
        first_year = float(np.min(year_values))
        last_year = float(np.max(year_values))
        span = max(last_year - first_year, 1.0)

        X = ((year_values - first_year) / span).reshape(-1, 1)
        y = df_clean['value'].values

        if len(X) == 0 or len(y) == 0:
            raise ValueError("Empty data for polynomial regression")

        max_allowed_degree = min(max_degree, max(2, len(df_clean) - 1), 6)
        degrees = list(range(2, max_allowed_degree + 1))

        candidates = []
        curvature_weight = 0.08
        value_scale = max(float(np.std(y)), float(np.mean(np.abs(y))), 1e-6)
        best_poly = None
        alpha_grid = [1.0, 0.3, 0.1, 0.03]
        for degree in degrees:
            for alpha in alpha_grid:
                model = make_pipeline(
                    PolynomialFeatures(degree=degree, include_bias=False),
                    Ridge(alpha=alpha),
                )
                label = f"Polynomial Regression (deg={degree}, α={alpha})"
                candidates.append(('poly', degree, model, label))

        if len(df_clean) >= 4:
            for gamma in [0.5, 1.0, 2.0, 5.0]:
                kr = KernelRidge(alpha=0.5, kernel='rbf', gamma=gamma)
                candidates.append(('kernel', None, kr, f"Kernel Ridge (gamma={gamma})"))

        if SplineTransformer is not None and len(df_clean) >= 4:
            knots = min(6, len(df_clean))
            spline_model = make_pipeline(
                SplineTransformer(n_knots=knots, degree=3, include_bias=False),
                Ridge(alpha=0.1),
            )
            candidates.append(('spline', None, spline_model, f"Spline Ridge (knots={knots})"))

        best_model = None
        best_label = ""
        best_score = float('inf')
        best_in_sample = None
        best_meta = {"kind": None, "degree": None, "curvature": 0.0}

        for kind, degree, model, label in candidates:
            try:
                model.fit(X, y)
            except Exception:
                continue
            preds = model.predict(X).reshape(-1)
            error = mean_squared_error(y, preds)
            curvature_metric = 0.0
            if len(preds) >= 3:
                second_diff = np.diff(preds, n=2)
                if len(second_diff) > 0:
                    curvature_metric = float(np.mean(np.abs(second_diff)))
            curvature_bonus = curvature_weight * (curvature_metric / value_scale)
            score = error - curvature_bonus
            candidate_info = {
                "kind": kind,
                "degree": degree,
                "model": model,
                "label": label,
                "score": score,
                "curvature": curvature_metric,
                "in_sample": preds.copy(),
            }

            if kind == 'poly':
                if (
                    best_poly is None
                    or score < best_poly['score'] - 1e-6
                    or (
                        abs(score - best_poly['score']) <= 1e-6
                        and degree is not None
                        and degree > (best_poly.get('degree') or 0)
                    )
                ):
                    best_poly = candidate_info

            if score < best_score - 1e-6:
                best_score = score
                best_model = model
                best_in_sample = preds
                best_label = label
                best_meta = {"kind": kind, "degree": degree, "curvature": curvature_metric}
            elif abs(score - best_score) <= 1e-6 and best_model is not None:
                prev_curvature = best_meta.get('curvature', 0.0)
                if curvature_metric > prev_curvature + 1e-6:
                    best_model = model
                    best_in_sample = preds
                    best_label = label
                    best_meta = {"kind": kind, "degree": degree, "curvature": curvature_metric}
                elif kind == 'poly' and degree is not None:
                    prev_degree = best_meta.get('degree')
                    if prev_degree is None or degree > prev_degree:
                        best_model = model
                        best_in_sample = preds
                        best_label = label
                        best_meta = {"kind": kind, "degree": degree, "curvature": curvature_metric}

        if best_model is None or best_in_sample is None:
            raise ValueError("Не удалось подобрать модель для прогноза")

        last_year_int = int(last_year)
        first_year_int = int(first_year)
        future_years = np.arange(first_year_int, last_year_int + periods + 1)

        future_features = ((future_years - first_year) / span).reshape(-1, 1)
        predictions = best_model.predict(future_features).reshape(-1)

        future_mask = future_years > last_year_int
        if (
            future_mask.any()
            and best_meta.get('kind') != 'poly'
            and best_poly is not None
        ):
            future_segment = predictions[future_mask]
            future_std = float(np.std(future_segment)) if len(future_segment) > 1 else 0.0
            if future_std < 1e-3 * value_scale:
                best_model = best_poly['model']
                best_in_sample = best_poly['in_sample']
                best_label = best_poly['label'] + " (extrapolation)"
                best_meta = {
                    "kind": "poly",
                    "degree": best_poly.get('degree'),
                    "curvature": best_poly.get('curvature', 0.0),
                }
                predictions = best_model.predict(future_features).reshape(-1)

        residuals = y - best_in_sample
        if len(residuals) > 1:
            std_error = np.std(residuals)
        else:
            std_error = max(np.abs(y).mean() * 0.15, 0.01)

        lower = predictions - 1.96 * std_error
        upper = predictions + 1.96 * std_error

        min_observed = float(np.min(y))
        if min_observed >= 0:
            predictions = np.clip(predictions, 0.0, None)
            lower = np.clip(lower, 0.0, None)

        result = pd.DataFrame(
            {
                'year': pd.to_datetime(future_years, format='%Y'),
                'forecast': predictions,
                'lower': lower,
                'upper': upper,
            }
        )

        return result, best_label

    def auto_forecast(self, df: pd.DataFrame, periods: int = 10) -> Tuple[pd.DataFrame, str]:
        if df.empty or len(df) < 3:
            raise ValueError("Недостаточно данных для прогнозирования (нужно минимум 3 точки)")
        
        if 'year' not in df.columns or 'value' not in df.columns:
            raise ValueError("DataFrame должен содержать колонки 'year' и 'value'")
        
        df_clean = df[['year', 'value']].dropna()
        
        if len(df_clean) < 3:
            raise ValueError("Недостаточно валидных данных после очистки")
        
        poly_error = None
        forecast_df = None
        method = ""

        try:
            forecast_df, method = self.forecast_polynomial(df_clean, periods)
        except Exception as e:
            poly_error = str(e)

        if forecast_df is None or forecast_df.empty:
            try:
                forecast_df = self.forecast_prophet(df_clean, periods)
                method = "Prophet (fallback after polynomial failure)"
            except Exception as prophet_error:
                fallback_reason = f"Polynomial error: {poly_error}; Prophet error: {str(prophet_error)}"
                raise ValueError(f"Ошибка прогнозирования: {fallback_reason}")

        if forecast_df.empty:
            raise ValueError("Прогноз не был сгенерирован")

        return forecast_df, method
    
    def calculate_metrics(self, actual: pd.Series, predicted: pd.Series) -> dict:
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        mae = np.mean(np.abs(actual - predicted))
        
        return {
            'MAPE': mape,
            'RMSE': rmse,
            'MAE': mae
        }


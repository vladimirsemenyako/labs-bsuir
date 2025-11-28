from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.data_loader import DataLoader
from src.forecasting import TimeSeriesForecaster
from src.config import DATASETS_CONFIG, RIVERS_BY, RIVER_COLORS
from src.rivers_geojson import RIVERS_GEOJSON

app = FastAPI(title="Water Resources API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_dir = os.path.join(project_root, 'data_clean')
loader = DataLoader(data_dir=data_dir)
forecaster = TimeSeriesForecaster()

CATEGORY_DEFAULT = "Реки"


def resolve_category_sources(category: Optional[str]):
    cat = category or CATEGORY_DEFAULT
    cat_normalized = cat.lower()
    if "подзем" in cat_normalized:
        return RIVERS_BY, RIVER_COLORS, RIVERS_GEOJSON, "Подземные воды"
    return RIVERS_BY, RIVER_COLORS, RIVERS_GEOJSON, "Реки"


def sort_categories(categories: List[str]) -> List[str]:
    filtered = [c for c in categories if c != 'Озера']
    order = ['Реки', 'Подземные воды']
    return sorted(
        filtered,
        key=lambda c: (order.index(c) if c in order else len(order), c)
    )

class ForecastRequest(BaseModel):
    filename: str
    entity: Optional[str] = None
    indicator: Optional[str] = None
    category: Optional[str] = None
    periods: int = 10

class ForecastResponse(BaseModel):
    historical: List[Dict]
    forecast: List[Dict]
    method: str

@app.get("/")
def read_root():
    return {"message": "Water Resources API", "version": "1.0"}


@app.get("/api/water/features")
def get_water_features(category: Optional[str] = CATEGORY_DEFAULT):
    mapping, colors, _, resolved = resolve_category_sources(category)
    features = [
        {
            "name": name,
            "lat": data["lat"],
            "lon": data["lon"],
            "color": colors.get(name, "#4B5563"),
        }
        for name, data in mapping.items()
    ]
    return {"category": resolved, "features": features}


@app.get("/api/water/geojson")
def get_water_geojson(category: Optional[str] = CATEGORY_DEFAULT):
    _, _, geojson, _ = resolve_category_sources(category)
    return geojson

@app.get("/api/datasets")
def get_datasets():
    return {
        "datasets": [
            {"filename": k, "title": v} 
            for k, v in DATASETS_CONFIG.items()
        ]
    }

@app.get("/api/dataset/{filename}")
def get_dataset_info(filename: str):
    try:
        df = loader.load_csv(filename)
        has_entities, entities, entity_type, indicators, categories = loader.detect_structure(df)
        categories = sort_categories(categories) if categories else []
        year_range = loader.get_year_range(df)
        
        category_entities = {}
        if categories and 'category' in df.columns and 'entity' in df.columns:
            for category in categories:
                subset = df[df['category'] == category]
                if subset.empty:
                    continue
                category_entities[category] = sorted(
                    subset['entity'].dropna().astype(str).unique().tolist()
                )

        return {
            "filename": filename,
            "title": DATASETS_CONFIG.get(filename, "Unknown"),
            "has_entities": has_entities,
            "entities": entities,
            "entity_type": entity_type,
            "indicators": indicators,
            "categories": categories,
            "category_entities": category_entities,
            "year_range": year_range
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/forecast", response_model=ForecastResponse)
def create_forecast(request: ForecastRequest):
    try:
        logger.info(
            "Forecast request: filename=%s, entity=%s, indicator=%s, category=%s, periods=%s",
            request.filename,
            request.entity,
            request.indicator,
            request.category,
            request.periods,
        )
        
        df = loader.load_csv(request.filename)
        logger.info(f"Loaded dataset: {len(df)} rows, {len(df.columns)} columns")
        
        if df.empty:
            logger.error("Dataset is empty")
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        ts_data = loader.prepare_timeseries(
            df,
            indicator=request.indicator,
            entity=request.entity,
            category=request.category,
        )
        logger.info(f"Prepared timeseries: {len(ts_data)} data points")
        
        if ts_data.empty:
            logger.error("No time series data available")
            raise HTTPException(status_code=400, detail="No time series data available. Try selecting a specific entity or indicator.")
        
        if len(ts_data) < 3:
            logger.error(f"Not enough data points: {len(ts_data)}")
            raise HTTPException(status_code=400, detail=f"Not enough data points (need at least 3, got {len(ts_data)})")
        
        forecast_df, method = forecaster.auto_forecast(ts_data, periods=request.periods)
        
        if forecast_df.empty:
            raise HTTPException(status_code=500, detail="Forecast failed to generate")
        
        historical = []
        for _, row in ts_data.iterrows():
            try:
                year_val = int(row['year'].year) if hasattr(row['year'], 'year') else int(row['year'])
                value_val = float(row['value'])
                historical.append({"year": year_val, "value": value_val})
            except Exception as e:
                continue
        
        if not historical:
            raise HTTPException(status_code=500, detail="Failed to process historical data")
        
        forecast = []
        for _, row in forecast_df.iterrows():
            try:
                year_val = int(row['year'].year) if hasattr(row['year'], 'year') else int(row['year'])
                forecast_val = float(row['forecast'])
                lower_val = float(row['lower'])
                upper_val = float(row['upper'])
                forecast.append({
                    "year": year_val,
                    "forecast": forecast_val,
                    "lower": lower_val,
                    "upper": upper_val
                })
            except Exception as e:
                continue
        
        if not forecast:
            raise HTTPException(status_code=500, detail="Failed to process forecast data")
        
        return {
            "historical": historical,
            "forecast": forecast,
            "method": method
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/api/entity-data/{filename}/{year}")
def get_entity_data(
    filename: str,
    year: int,
    indicator: Optional[str] = None,
    category: Optional[str] = None,
):
    try:
        df = loader.load_csv(filename)
        has_entities, entities, entity_type, indicators, categories = loader.detect_structure(df)
        
        if not has_entities:
            return {"entities": {}, "type": entity_type}

        if category and 'category' in df.columns:
            cat_entities = df[df['category'] == category]['entity'].dropna().astype(str).unique().tolist()
            if cat_entities:
                entities = sorted(cat_entities)
        
        entity_values, resolved_year = loader.get_entity_data(
            df,
            year,
            entities,
            indicator=indicator,
            category=category,
        )
        
        return {
            "entities": entity_values,
            "type": entity_type,
            "year": resolved_year,
            "requested_year": year,
            "categories": categories,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rivers")
def get_rivers():
    return {
        "rivers": [
            {
                "name": name,
                "lat": coords["lat"],
                "lon": coords["lon"],
                "color": RIVER_COLORS.get(name, "#808080")
            }
            for name, coords in RIVERS_BY.items()
        ]
    }

@app.get("/api/rivers/geojson")
def get_rivers_geojson():
    return RIVERS_GEOJSON

@app.get("/api/debug/dataset/{filename}")
def debug_dataset(filename: str):
    try:
        df = loader.load_csv(filename)
        rows_with_data = loader.get_all_rows_with_data(df)
        
        return {
            "shape": df.shape,
            "columns": list(df.columns)[:20],
            "rows_with_data": rows_with_data[:20]
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/timeseries/{filename}")
def get_timeseries(
    filename: str,
    entity: Optional[str] = None,
    indicator: Optional[str] = None,
    category: Optional[str] = None,
):
    try:
        df = loader.load_csv(filename)
        ts_data = loader.prepare_timeseries(
            df, indicator=indicator, entity=entity, category=category
        )
        
        if ts_data.empty:
            return {"data": []}
        
        data = [
            {"year": int(row['year'].year), "value": float(row['value'])}
            for _, row in ts_data.iterrows()
        ]
        
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from src.data_loader import DataLoader

loader = DataLoader(data_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data_clean'))

print("Testing C1-1990-2023.csv")
df = loader.load_csv('C1-1990-2023.csv')
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst few rows:")
print(df.head())

has_entities, entities, entity_type, indicators, categories = loader.detect_structure(df)
print(f"\nIndicators found: {len(indicators)}")
for i, ind in enumerate(indicators[:10]):
    print(f"  {i+1}. {ind}")

print("\n\nTrying to get timeseries without filter:")
ts = loader.prepare_timeseries(df)
print(f"Result: {len(ts)} points")
if not ts.empty:
    print(ts.head())
else:
    print("EMPTY!")

if indicators:
    print(f"\n\nTrying with indicator: {indicators[0]}")
    ts = loader.prepare_timeseries(df, indicator=indicators[0])
    print(f"Result: {len(ts)} points")
    if not ts.empty:
        print(ts.head())


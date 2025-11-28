import csv
import os

files = [
    'C3-1990-2024.csv', 
    'C4-2001-2024.csv', 
    'C6-2005-2025.csv', 
    'C10-2005-2024.csv', 
    'С14-2005-2025.csv',
    'C16-2005-2024.csv'
]

for filename in files:
    filepath = os.path.join('data', filename)
    print(f"\n{'='*80}")
    print(f"File: {filename}")
    print('='*80)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i < 15:
                    print(f"Row {i}: {row[:5]} ...")
                else:
                    break
    except Exception as e:
        print(f"Error: {e}")


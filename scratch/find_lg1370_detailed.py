import pandas as pd
import os

file_path = '/home/hsinwei/app/mes/鑄件盤點資料.xlsx'
xl = pd.ExcelFile(file_path, engine='openpyxl')

for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    # Search for LG1370
    mask = df.astype(str).apply(lambda x: x.str.contains('LG1370|LG-1370', case=False)).any(axis=1)
    if mask.any():
        print(f"\n--- {sheet} ---")
        cols = [c for c in ['品號', '機型'] if c in df.columns]
        if not cols:
            cols = df.columns[:2].tolist()
        print(df[mask][cols])

import pandas as pd
import os

file_path = '/home/hsinwei/app/mes/鑄件盤點資料.xlsx'
xl = pd.ExcelFile(file_path, engine='openpyxl')

for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    # Search for anything containing 8811
    mask = df.astype(str).apply(lambda x: x.str.contains('8811', case=False)).any(axis=1)
    if mask.any():
        print(f"\n--- {sheet} ---")
        print(df[mask][df.columns[:2]])

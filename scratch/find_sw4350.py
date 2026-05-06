import pandas as pd
import os

file_path = '/home/hsinwei/app/mes/鑄件盤點資料.xlsx'
xl = pd.ExcelFile(file_path, engine='openpyxl')
found = False
for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    if df.astype(str).apply(lambda x: x.str.contains('SW4350', case=False)).any().any():
        print(f"Found SW4350 in sheet: {sheet}")
        found = True

if not found:
    print("SW4350 not found in any sheet")

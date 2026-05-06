import pandas as pd
import os

file_path = '/home/hsinwei/app/mes/鑄件盤點資料.xlsx'
if not os.path.exists(file_path):
    print("File not found")
    exit(1)

xl = pd.ExcelFile(file_path, engine='openpyxl')
found = False
for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    # Check all cells for SW4320 or lg1370
    if df.astype(str).apply(lambda x: x.str.contains('SW4320|LG1370', case=False)).any().any():
        print(f"Found match in sheet: {sheet}")
        found = True

if not found:
    print("Not found in any sheet")

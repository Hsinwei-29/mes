import pandas as pd

f = '鑄件盤點資料.xlsx'
xl = pd.ExcelFile(f, engine='openpyxl')
for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    for col in df.columns:
        mask = df[col].astype(str).str.contains('980000028600')
        row = df[mask]
        if not row.empty:
            print(f"Part 980000028600 found in sheet '{sheet}', col '{col}':")
            print(row.to_string())

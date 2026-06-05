import pandas as pd

f = '鑄件盤點資料.xlsx'
xl = pd.ExcelFile(f, engine='openpyxl')
for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    # Search for 'HSA-320' or '320' in any column
    mask = df.apply(lambda x: x.astype(str).str.contains('HSA-320', case=False)).any(axis=1)
    row = df[mask]
    if not row.empty:
        print(f"Found in sheet '{sheet}':")
        print(row.to_string())

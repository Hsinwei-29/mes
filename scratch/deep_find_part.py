import pandas as pd

f = '鑄件盤點資料.xlsx'
xl = pd.ExcelFile(f, engine='openpyxl')
for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    # Search for '8817000552' in all columns
    for col in df.columns:
        mask = df[col].astype(str).str.contains('8817000552')
        row = df[mask]
        if not row.empty:
            print(f"Found 8817000552 in sheet '{sheet}', column '{col}':")
            print(row.to_string())

import pandas as pd

f = '鑄件盤點資料.xlsx'
xl = pd.ExcelFile(f, engine='openpyxl')
for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    for col in df.columns:
        # Try numeric match
        try:
            mask = (df[col] == 8817000552)
            row = df[mask]
            if not row.empty:
                print(f"Exact numeric match 8817000552 in sheet '{sheet}', col '{col}':")
                print(row.to_string())
        except:
            pass

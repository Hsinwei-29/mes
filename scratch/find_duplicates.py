import pandas as pd

file_path = '/home/hsinwei/app/mes/鑄件盤點資料.xlsx'
xl = pd.ExcelFile(file_path, engine='openpyxl')

for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    # Some sheets might use column index 1 for model
    model_col = '機型' if '機型' in df.columns else (df.columns[1] if len(df.columns) > 1 else None)
    
    if model_col:
        counts = df[model_col].dropna().astype(str).str.strip().value_counts()
        dupes = counts[counts > 1]
        if not dupes.empty:
            print(f"\n--- {sheet} ---")
            print(dupes)

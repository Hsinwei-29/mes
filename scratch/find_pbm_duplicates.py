import pandas as pd

file_path = '/home/hsinwei/app/mes/鑄件盤點資料.xlsx'
xl = pd.ExcelFile(file_path, engine='openpyxl')

for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    model_col = '機型' if '機型' in df.columns else (df.columns[1] if len(df.columns) > 1 else None)
    
    if model_col:
        mask = df[model_col].astype(str).str.contains('PBM', case=False)
        if mask.any():
            print(f"\n--- {sheet} ---")
            models = df[mask][model_col].dropna().tolist()
            print(models)
            counts = pd.Series(models).value_counts()
            dupes = counts[counts > 1]
            if not dupes.empty:
                print("Duplicates found in sheet:")
                print(dupes)

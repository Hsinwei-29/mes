import pandas as pd
import glob
import os

files = glob.glob('*.xls*')
for f in files:
    try:
        engine = 'calamine' if f.endswith('.xls') else 'openpyxl'
        xl = pd.ExcelFile(f, engine=engine)
        for sheet in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet)
            mask = df.astype(str).apply(lambda x: x.str.contains('100003314')).any(axis=1)
            if mask.any():
                print(f"Found in {f}, sheet {sheet}")
    except Exception as e:
        print(f"Error reading {f}: {e}")

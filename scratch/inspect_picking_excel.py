import pandas as pd
import os

excel_file = '/home/hsinwei/app/mes/成品撥料.XLSX'
print(f"Checking {excel_file}...")

if os.path.exists(excel_file):
    try:
        # Load first sheet
        df = pd.read_excel(excel_file, nrows=5)
        print("Columns in 成品撥料.XLSX:")
        print(df.columns.tolist())
        
        # Load total rows (only count)
        df_full = pd.read_excel(excel_file, usecols=[0])
        print(f"Total rows in 成品撥料.XLSX: {len(df_full)}")
        
    except Exception as e:
        print(f"Error: {e}")
else:
    print("File does not exist!")

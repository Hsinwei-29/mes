import pandas as pd
import os

file_path = r'd:\app\mes\工單總表2026.xls'
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit()

xl = pd.ExcelFile(file_path)
print(f"Sheets: {xl.sheet_names}")

for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    print(f"\nSheet: {sheet}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print("Top 5 rows:")
    print(df.head())
    
    if sheet == '工單總表':
        print("\nChecking for empty '工單號碼' in '工單總表':")
        # Identify rows that might be skipped but have other data
        skipped = df[df['工單號碼'].isna()]
        print(f"Rows with NaN '工單號碼': {len(skipped)}")
        # Check if any skipped row has '訂單號碼' or '品號說明'
        meaningful_skipped = skipped[skipped['訂單號碼'].notna() | skipped['品號說明'].notna()]
        print(f"Meaningful skipped rows (has order num or description): {len(meaningful_skipped)}")
        if len(meaningful_skipped) > 0:
            print("Example meaningful skipped rows:")
            print(meaningful_skipped.head())
        else:
            print("All NaN rows seem to be truly empty or footer rows.")
        
        # Check for rows that might fail conversion
        for idx, val in df['工單號碼'].items():
            if pd.notna(val):
                try:
                    _ = int(float(val))
                except Exception as e:
                    print(f"Row {idx} conversion failed for value {val}: {e}")

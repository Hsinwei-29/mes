# -*- coding: utf-8 -*-
import pandas as pd

print("=== 工單總表2026.xls ===")
xl = pd.ExcelFile(r'd:\app\mes\工單總表2026.xls')
print("Sheet names:", xl.sheet_names)

for sheet in xl.sheet_names[:3]:  # 只看前3個分頁
    print(f"\n--- Sheet: {sheet} ---")
    df = pd.read_excel(xl, sheet_name=sheet)
    print("Columns:", df.columns.tolist())
    print("Shape:", df.shape)
    print("First 5 rows:")
    print(df.head())

# 保存結構到檔案
with open(r'd:\app\mes\workorder_structure.txt', 'w', encoding='utf-8') as f:
    f.write("=== 工單總表2026.xls ===\n")
    f.write(f"Sheet names: {xl.sheet_names}\n\n")
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet)
        f.write(f"\n--- Sheet: {sheet} ---\n")
        f.write(f"Columns: {df.columns.tolist()}\n")
        f.write(f"Shape: {df.shape}\n")
        f.write("First 5 rows:\n")
        for i in range(min(5, len(df))):
            row = df.iloc[i].to_dict()
            f.write(f"Row {i}: {row}\n")

print("\n\nStructure saved to d:\\app\\mes\\workorder_structure.txt")

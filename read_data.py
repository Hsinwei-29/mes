# -*- coding: utf-8 -*-
import pandas as pd
import json

# Read 鑄件盤點資料.xlsx
print("=== 鑄件盤點資料.xlsx ===")
xl = pd.ExcelFile(r'd:\app\mes\鑄件盤點資料.xlsx')
print("Sheet names:", xl.sheet_names)

df = pd.read_excel(xl)
print("\nColumns:", df.columns.tolist())
print("Shape:", df.shape)

# Print data types
print("\nData types:")
print(df.dtypes)

# Print unique values in first column (品號)
print("\nUnique values in first column (品號):")
print(df.iloc[:, 0].unique()[:20].tolist())

# Check all sheets
print("\n\n=== Checking all sheets ===")
for sheet in xl.sheet_names:
    df_sheet = pd.read_excel(xl, sheet_name=sheet)
    print(f"\nSheet: {sheet}")
    print(f"  Columns: {df_sheet.columns.tolist()}")
    print(f"  Shape: {df_sheet.shape}")

# Save column info to file for later reference
with open(r'd:\app\mes\data_structure.txt', 'w', encoding='utf-8') as f:
    f.write("=== 鑄件盤點資料.xlsx ===\n")
    f.write(f"Sheet names: {xl.sheet_names}\n")
    f.write(f"Columns: {df.columns.tolist()}\n")
    f.write(f"Shape: {df.shape}\n\n")
    
    f.write("First 20 rows data:\n")
    for i in range(min(20, len(df))):
        row = df.iloc[i].to_dict()
        f.write(f"Row {i}: {row}\n")
    
    xl2 = pd.ExcelFile(r'd:\app\mes\成品入庫TECO狀態.XLSX')
    f.write("\n\n=== 成品入庫TECO狀態.XLSX ===\n")
    f.write(f"Sheet names: {xl2.sheet_names}\n")
    df2 = pd.read_excel(xl2)
    f.write(f"Columns: {df2.columns.tolist()}\n")
    f.write(f"Shape: {df2.shape}\n\n")
    
    f.write("First 10 rows data:\n")
    for i in range(min(10, len(df2))):
        row = df2.iloc[i].to_dict()
        f.write(f"Row {i}: {row}\n")

print("\n\nData structure saved to d:\\app\\mes\\data_structure.txt")

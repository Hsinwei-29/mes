# -*- coding: utf-8 -*-
import pandas as pd

file_path = r'd:\app\mes\成品撥料.XLSX'
print(f"=== Reading {file_path} ===")

try:
    df = pd.read_excel(file_path)
    print("Columns:", df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head())
    
    # 檢查 B, E, I 欄位 (索引 1, 4, 8)
    print("\nTarget Columns Check:")
    if len(df.columns) > 8:
        print(f"Col B (Index 1): {df.columns[1]}")
        print(f"Col E (Index 4): {df.columns[4]}")
        print(f"Col I (Index 8): {df.columns[8]}")
        
    # 顯示物料欄位的唯一值範例，幫助判斷如何分類
    col_b_name = df.columns[1]
    print(f"\nSample values in '{col_b_name}':")
    print(df[col_b_name].unique()[:20])
    
except Exception as e:
    print(f"Error: {e}")

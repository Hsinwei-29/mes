# -*- coding: utf-8 -*-
import pandas as pd

# 讀取檔案
df = pd.read_excel(r'd:\app\mes\成品撥料.XLSX')

# 保存結構到檔案
with open(r'd:\app\mes\picking_structure.txt', 'w', encoding='utf-8') as f:
    f.write("=== 成品撥料.XLSX ===\n")
    f.write(f"Columns: {df.columns.tolist()}\n")
    f.write(f"Shape: {df.shape}\n")
    f.write("\nFirst 10 rows:\n")
    for i in range(min(10, len(df))):
        row = df.iloc[i].to_dict()
        f.write(f"Row {i}: {row}\n")

print("Done")

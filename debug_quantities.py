import pandas as pd
import os

file_path = r'd:\app\mes\工單總表2026.xls'
xl = pd.ExcelFile(file_path)

# Dictionary to map garbled names if possible, but easier to use index
df = pd.read_excel(xl, sheet_name='工單總表')
print("Columns in '工單總表':")
for i, col in enumerate(df.columns):
    print(f"Index {i}: {col}")

print("\nFirst 10 rows of '工單總表' (selected columns):")
# Assuming index 1 is Work Order, index 2 is Order Number, index 10-14 are quantities/status
cols_to_show = [1, 2, 4, 10, 11, 12, 13, 14]
print(df.iloc[:10, cols_to_show])

print("\nSums of potential quantity columns:")
for i in range(10, 15):
    try:
        s = df.iloc[:, i].sum()
        print(f"Column {i} sum: {s}")
    except:
        pass

print("\nChecking '半品總表':")
df_semi = pd.read_excel(xl, sheet_name='半品總表')
print(f"Semi-finished orders count: {len(df_semi[df_semi.iloc[:, 0].notna()])}")

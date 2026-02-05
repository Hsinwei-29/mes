import pandas as pd

CASTING_FILE = r'D:\app\mes\鑄件盤點資料.xlsx'

xl = pd.ExcelFile(CASTING_FILE)

for part_name, sheet_idx in [('底座', 1), ('工作台', 2), ('橫樑', 3), ('立柱', 4)]:
    df = pd.read_excel(xl, sheet_name=sheet_idx)
    
    print(f"\n{part_name} (Sheet {sheet_idx}):")
    print("  欄位列表:")
    for i, col in enumerate(df.columns):
        print(f"    [{i}] {col}")
    
    # 尋找「總」字的欄位
    total_cols = [i for i, col in enumerate(df.columns) if '總' in str(col)]
    if total_cols:
        print(f"  包含'總'的欄位索引: {total_cols}")
        for idx in total_cols:
            print(f"    索引 {idx}: {df.columns[idx]}")

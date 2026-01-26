import pandas as pd

# 測試新的求和邏輯
casting_file = '鑄件盤點資料.xlsx'
xl = pd.ExcelFile(casting_file)

inventory = {}
for part_name, sheet_idx in [('底座', 1), ('工作台', 2), ('橫樑', 3), ('立柱', 4)]:
    try:
        df = pd.read_excel(xl, sheet_name=sheet_idx)
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        print(f"\n{part_name} (工作表 {sheet_idx}):")
        print(f"  數字列: {numeric_cols[:5]}")
        
        # 對所有數字列求和（排除第一列品號）
        total = 0
        if len(numeric_cols) > 1:
            for col in numeric_cols[1:]:  # 跳過第一個數字列（品號）
                col_sum = df[col].sum()
                if not pd.isna(col_sum):
                    print(f"  {col}: {col_sum}")
                    total += col_sum
        inventory[part_name] = int(total) if total > 0 else 0
        print(f"  總計: {inventory[part_name]}")
    except Exception as e:
        print(f"  錯誤: {e}")
        inventory[part_name] = 0

print(f"\n最終結果: {inventory}")

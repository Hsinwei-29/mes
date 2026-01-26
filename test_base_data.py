import pandas as pd

# 測試讀取底座工作表
print("=" * 60)
print("測試底座工作表數據讀取")
print("=" * 60)

df = pd.read_excel('鑄件盤點資料.xlsx', sheet_name=1)  # 底座
print(f"\n形狀: {df.shape}")
print(f"\n列名: {df.columns.tolist()}")

# 找出數字列
numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
print(f"\n數字列: {numeric_cols}")

# 計算總數
total = 0
for col in numeric_cols:
    col_sum = df[col].sum()
    if not pd.isna(col_sum) and col_sum > 0:
        print(f"{col}: {col_sum}")
        total += col_sum

print(f"\n底座總數: {int(total)}")

# 顯示前5行
print("\n前5行數據:")
print(df.head())

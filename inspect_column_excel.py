import pandas as pd

CASTING_FILE = r'D:\app\mes\鑄件盤點資料.xlsx'

xl = pd.ExcelFile(CASTING_FILE)

# 讀取立柱工作表 (索引 4)
df = pd.read_excel(xl, sheet_name=4)

print("立柱工作表的所有欄位：")
for i, col in enumerate(df.columns):
    print(f"  [{i}] {col}")

print(f"\n立柱工作表的所有資料（前15行）：")
print(df.head(15).to_string())

# 檢查索引 6 的欄位
if len(df.columns) > 6:
    col_6 = df.columns[6]
    print(f"\n索引 6 的欄位名稱: {col_6}")
    print(f"索引 6 的所有非空值:")
    for idx, row in df.iterrows():
        val = row.iloc[6]
        if pd.notna(val) and val != 0:
            model = row.iloc[1] if len(row) > 1 else 'N/A'
            print(f"  行 {idx}: {model} = {val}")
    
    # 計算總和
    total = 0
    for idx, row in df.iterrows():
        val = row.iloc[6]
        if pd.notna(val):
            try:
                total += int(float(val))
            except:
                pass
    print(f"\n索引 6 欄位的總和: {total}")

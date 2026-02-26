import pandas as pd
import sys

# 測試讀取 Excel 檔案
print("=" * 60)
print("測試 Excel 檔案讀取")
print("=" * 60)

try:
    # 讀取總數工作表
    df = pd.read_excel('鑄件盤點資料.xlsx', sheet_name='總數')
    
    print(f"\n資料形狀: {df.shape[0]} 行 x {df.shape[1]} 列")
    print(f"\n列名: {df.columns.tolist()}")
    
    # 檢查每一列的數據
    print("\n前 5 行數據:")
    print(df.head())
    
    # 檢查數據類型
    print("\n數據類型:")
    print(df.dtypes)
    
    # 檢查是否有數據
    print("\n各列總和:")
    for col in df.columns:
        if col not in ['機型']:
            total = df[col].sum()
            print(f"{col}: {total}")
    
    # 檢查 NaN 值
    print("\n各列 NaN 數量:")
    print(df.isna().sum())
    
    # 檢查實際數值
    print("\n第一行實際數值:")
    print(df.iloc[0].to_dict())
    
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()

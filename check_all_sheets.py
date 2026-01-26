import pandas as pd

print("=" * 60)
print("檢查所有工作表")
print("=" * 60)

try:
    xl = pd.ExcelFile('鑄件盤點資料.xlsx')
    print(f"\n工作表列表: {xl.sheet_names}\n")
    
    for sheet_name in xl.sheet_names:
        print(f"\n{'='*40}")
        print(f"工作表: {sheet_name}")
        print(f"{'='*40}")
        
        df = pd.read_excel(xl, sheet_name=sheet_name)
        print(f"形狀: {df.shape}")
        print(f"列名: {df.columns.tolist()[:10]}")  # 只顯示前10個列名
        
        # 檢查是否有數據
        non_null_count = df.notna().sum().sum()
        total_cells = df.shape[0] * df.shape[1]
        print(f"非空值數量: {non_null_count} / {total_cells}")
        
        # 顯示前3行
        print("\n前3行:")
        print(df.head(3))
        
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()

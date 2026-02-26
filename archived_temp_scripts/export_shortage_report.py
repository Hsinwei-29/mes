"""生成缺料報表並匯出到 Excel"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
from datetime import datetime

from app import create_app
from app.models.shortage import calculate_shortage

# 建立應用程式上下文
app = create_app()
app.app_context().push()

print("正在計算缺料...")
shortage_result = calculate_shortage()

# 轉換為 DataFrame
df = pd.DataFrame(shortage_result)

# 格式化日期欄位
if '生產開始' in df.columns:
    df['生產開始'] = pd.to_datetime(df['生產開始']).dt.strftime('%Y-%m-%d')
if '生產結束' in df.columns:
    df['生產結束'] = pd.to_datetime(df['生產結束']).dt.strftime('%Y-%m-%d')

# 調整欄位順序
column_order = [
    '工單號碼', '客戶名稱', '生產開始', '生產結束',
    '品號', '物料說明', '零件類型',
    '需求數量', '已領料', '目前缺料', '現有庫存', '缺料數量', '狀態'
]
df = df[column_order]

# 生成檔案名稱
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'缺料分析報表_{timestamp}.xlsx'

# 匯出到 Excel
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # 所有記錄
    df.to_excel(writer, sheet_name='全部記錄', index=False)
    
    # 只有缺料的記錄
    shortage_only = df[df['缺料數量'] > 0]
    shortage_only.to_excel(writer, sheet_name='缺料清單', index=False)
    
    # 按零件類型分類
    for part_type in ['工作台', '底座', '橫樑', '立柱']:
        part_df = df[df['零件類型'] == part_type]
        if not part_df.empty:
            part_df.to_excel(writer, sheet_name=f'{part_type}', index=False)

print(f'\n報表已匯出: {output_file}')
print(f'總記錄數: {len(df)}')
print(f'缺料項目: {len(shortage_only)}')
print(f'\n按零件類型統計:')
for part_type in ['工作台', '底座', '橫樑', '立柱']:
    count = len(df[df['零件類型'] == part_type])
    shortage_count = len(df[(df['零件類型'] == part_type) & (df['缺料數量'] > 0)])
    print(f'  {part_type}: {count} 筆 (缺料 {shortage_count} 筆)')

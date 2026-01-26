import pandas as pd
import os

workorder_file = r'd:\app\mes\工單總表2026.xls'
picking_file = r'd:\app\mes\成品撥料.XLSX'

def clean_order_id(val):
    if pd.isna(val): return None
    # Handle scientific notation by converting to float then int then string
    try:
        f_val = float(val)
        return str(int(f_val)).strip()
    except:
        return str(val).strip()

# 1. 讀取撥料單訂單
df_picking = pd.read_excel(picking_file, usecols=[0])
picking_orders = set(df_picking.iloc[:, 0].apply(clean_order_id).dropna())
print(f"Unique orders in Picking List: {len(picking_orders)}")

# 2. 檢索工單檔案所有分頁 (除半品)
xl = pd.ExcelFile(workorder_file)
all_wo_orders = {}

for sheet in xl.sheet_names:
    if '半品' in sheet: continue
    
    df = pd.read_excel(xl, sheet_name=sheet)
    # 尋找訂單號碼欄位 (通常是第 2 或第 3 欄)
    # 我們遍歷所有欄位，只要內容看起來像訂單號碼 (9-10位數字)
    sheet_orders = set()
    for col in df.columns:
        valid_orders = df[col].apply(clean_order_id).dropna()
        # 過濾看起來像訂單的串 (假設至少 8 位數)
        filtered = [v for v in valid_orders if v.isdigit() and len(v) >= 8]
        sheet_orders.update(filtered)
    
    all_wo_orders[sheet] = sheet_orders
    print(f"Sheet '{sheet}': found {len(sheet_orders)} unique order IDs.")

# 3. 匯總
combined_wo_orders = set()
for s_orders in all_wo_orders.values():
    combined_wo_orders.update(s_orders)

print(f"\nCombined Unique Orders (excluding semi-finished): {len(combined_wo_orders)}")

# 4. 比對撥料單
intersect = picking_orders.intersection(combined_wo_orders)
missing = picking_orders - combined_wo_orders

print(f"Matched with Picking List: {len(intersect)}")
print(f"Missing from Picking List: {len(missing)}")

if len(missing) > 0:
    print(f"Example Missing: {list(missing)[:5]}")

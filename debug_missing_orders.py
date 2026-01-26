import pandas as pd
import os

workorder_file = r'd:\app\mes\工單總表2026.xls'
picking_file = r'd:\app\mes\成品撥料.XLSX'

# 1. 讀取撥料單中的所有訂單
print("--- Picking Data Analysis ---")
df_picking = pd.read_excel(picking_file, usecols=[0])
df_picking.columns = ['訂單']
picking_orders = set(df_picking['訂單'].dropna().astype(str).str.strip())
print(f"Unique orders in Picking List: {len(picking_orders)}")

# 2. 讀取工單總表中的所有訂單
print("\n--- Work Order Data Analysis ---")
df_wo = pd.read_excel(workorder_file, sheet_name='工單總表')
# 找出所有可能的訂單號碼欄位 (嘗試處理亂碼或名稱差異)
order_cols = [col for col in df_wo.columns if '訂單' in str(col) or 'q' in str(col)]
print(f"Potential Order columns in WO: {order_cols}")

wo_orders = set()
for col in order_cols:
    wo_orders.update(df_wo[col].dropna().astype(str).str.strip())
print(f"Unique orders in Work Order list: {len(wo_orders)}")

# 3. 比對差距
missing_in_wo = picking_orders - wo_orders
print(f"\nOrders in Picking but MISSING in Work Order List: {len(missing_in_wo)}")
if len(missing_in_wo) > 0:
    print(f"Example missing orders: {list(missing_in_wo)[:5]}")

# 4. 尋找數量欄位
print("\n--- Columns Peek ---")
print(df_wo.columns.tolist())
# 看看有沒有像數量的值 (通常是小整數)
for col in df_wo.columns:
    sample = df_wo[col].dropna()
    if len(sample) > 0 and pd.api.types.is_numeric_dtype(sample):
        if sample.max() < 1000 and sample.mean() < 50:
            print(f"Possible Quantity Column: {col} (Mean: {sample.mean():.2f})")

import pandas as pd

f = '工單總表2026.xls'
df = pd.read_excel(f, engine='calamine')
mask = df.apply(lambda x: x.astype(str).str.contains('HSA-320', case=False)).any(axis=1)
row = df[mask]
if not row.empty:
    print("HSA-320 found in Work Order Excel:")
    print(row[['工單號碼', '物料品號', '品號說明']].to_string())
else:
    print("HSA-320 not found in Work Order Excel")

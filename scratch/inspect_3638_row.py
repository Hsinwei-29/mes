import pandas as pd

f = '工單總表2026.xls'
df = pd.read_excel(f, engine='calamine')
row = df[df['工單號碼'].astype(str).str.contains('100003638')]

if not row.empty:
    for col in df.columns:
        print(f"{col}: {row.iloc[0][col]}")
else:
    print("Not found")

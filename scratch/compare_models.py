import pandas as pd
import os
import sys

sys.path.append('/home/hsinwei/app/mes')
from app.models.inventory import normalize_model_name

file_path = '/home/hsinwei/app/mes/鑄件盤點資料.xlsx'
xl = pd.ExcelFile(file_path, engine='openpyxl')

# 1. Get Summary models
df_summary = pd.read_excel(xl, sheet_name='總數')
summary_models = df_summary['機型'].dropna().astype(str).str.strip().tolist()

# 2. Get all models from other sheets
other_models = {}
for sheet in ['底座', '工作台', '橫樑', '立柱', '定樑']:
    df = pd.read_excel(xl, sheet_name=sheet)
    model_col = '機型' if '機型' in df.columns else (df.columns[1] if len(df.columns) > 1 else None)
    if model_col:
        models = df[model_col].dropna().astype(str).str.strip().tolist()
        for m in models:
            if m not in other_models:
                other_models[m] = []
            other_models[m].append(sheet)

print(f"Summary sheet has {len(summary_models)} models.")
print(f"Other sheets have {len(other_models)} unique models.")

# Check what's in other sheets but NOT in summary
missing_in_summary = []
for m in other_models:
    if m not in summary_models:
        missing_in_summary.append(m)

print(f"\nModels in parts sheets but NOT in Summary sheet ({len(missing_in_summary)}):")
for m in missing_in_summary[:20]:
    print(f"- {m} (found in {other_models[m]})")
if len(missing_in_summary) > 20:
    print("...")

# Check normalized duplicates
norm_map = {}
for m in summary_models:
    norm = normalize_model_name(m)
    if norm in norm_map:
        print(f"Conflict in Summary: {m} and {norm_map[norm]} both normalize to {norm}")
    norm_map[norm] = m

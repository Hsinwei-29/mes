import pandas as pd
from flask import current_app
from openpyxl import load_workbook
from datetime import datetime
import json
import os

def load_casting_inventory():
    """載入鑄件庫存資料 - 從各個工作表計算總數"""
    try:
        casting_file = current_app.config['CASTING_FILE']
        xl = pd.ExcelFile(casting_file)
        
        # 工作表索引：底座=1, 工作台=2, 橫樑=3, 立柱=4
        sheet_mapping = {'底座': 1, '工作台': 2, '橫樑': 3, '立柱': 4}
        
        inventory = {}
        all_details = {}
        
        for part_name, sheet_idx in sheet_mapping.items():
            try:
                df = pd.read_excel(xl, sheet_name=sheet_idx)
                
                # 計算總數：所有數字列的總和
                total = 0
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                for col in numeric_cols:
                    col_sum = df[col].sum()
                    if not pd.isna(col_sum):
                        total += int(col_sum)
                
                inventory[part_name] = total
                
                # 儲存該工作表的詳細資料（用於後續的 details 整合）
                all_details[part_name] = df
                
            except Exception as e:
                print(f"Error loading {part_name}: {e}")
                inventory[part_name] = 0
        
        # 確保順序
        inventory = {
            '工作台': inventory.get('工作台', 0),
            '底座': inventory.get('底座', 0),
            '橫樑': inventory.get('橫樑', 0),
            '立柱': inventory.get('立柱', 0)
        }
        
        # 整合詳細資料（按機型）
        details = []
        # 從工作台工作表提取機型列表
        if '工作台' in all_details and '機型' in all_details['工作台'].columns:
            for _, row in all_details['工作台'].iterrows():
                model = row.get('機型', '')
                if pd.notna(model) and str(model).strip():
                    detail = {'機型': str(model)}
                    # 為每個鑄件類型設置數量（簡化版本，只顯示工作台的數據）
                    for part in ['工作台', '底座', '橫樑', '立柱']:
                        detail[part] = 0
                    
                    # 計算工作台的總數
                    total_for_model = 0
                    for col in numeric_cols:
                        val = row.get(col, 0)
                        if pd.notna(val):
                            total_for_model += int(val)
                    
                    detail['工作台'] = total_for_model
                    
                    if total_for_model > 0:
                        details.append(detail)
        
        return {'summary': inventory, 'details': details}
        
    except Exception as e:
        print(f"Error loading casting inventory: {e}")
        import traceback
        traceback.print_exc()
        return {'summary': {}, 'details': [], 'error': str(e)}

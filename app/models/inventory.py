import pandas as pd
from flask import current_app
from openpyxl import load_workbook
from datetime import datetime
import json
import os

def load_casting_inventory():
    """載入鑄件庫存資料"""
    try:
        casting_file = current_app.config['CASTING_FILE']
        xl = pd.ExcelFile(casting_file)
        
        # 從各個鑄件工作表計算總數
        inventory = {}
        all_models = {}  # 儲存所有機型的數據
        
        for part_name, sheet_idx in [('底座', 1), ('工作台', 2), ('橫樑', 3), ('立柱', 4)]:
            try:
                df = pd.read_excel(xl, sheet_name=sheet_idx)
                
                # 找出所有數字列
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                # 排除品號列（第一個數字列，值通常很大）
                sum_cols = []
                for col in numeric_cols:
                    # 跳過 Unnamed 列
                    if 'Unnamed' in str(col):
                        continue
                    
                    # 檢查該列的最大值，如果超過 1000000，可能是品號
                    max_val = df[col].max()
                    if pd.notna(max_val) and max_val > 1000000:
                        continue
                    
                    # 檢查該列是否有實際數據（不全是 NaN 或 0）
                    col_sum = df[col].sum()
                    if pd.isna(col_sum):
                        continue
                        
                    sum_cols.append(col)
                
                # 計算總數
                total = 0
                for col in sum_cols:
                    col_sum = df[col].sum()
                    if not pd.isna(col_sum):
                        total += col_sum
                
                inventory[part_name] = int(total) if total > 0 else 0
                
                # 提取機型詳細資料
                if '機型' in df.columns:
                    # 取得成品欄位索引（總數前一個欄位）
                    config = CONFIGS.get(part_name, [])
                    finished_col_idx = None
                    if len(config) >= 2:
                        # 取倒數第二個配置（總數前一個，即成品）
                        finished_col_idx = config[-2][1]
                    
                    for _, row in df.iterrows():
                        model = row.get('機型', '')
                        if pd.notna(model) and str(model).strip():
                            model_str = str(model).strip()
                            
                            # 初始化該機型的數據
                            if model_str not in all_models:
                                all_models[model_str] = {'機型': model_str, '工作台': 0, '底座': 0, '橫樑': 0, '立柱': 0}
                            
                            # 使用成品欄位的數量
                            finished_value = 0
                            if finished_col_idx is not None:
                                val = row.iloc[finished_col_idx]
                                if pd.notna(val):
                                    try:
                                        finished_value = int(float(val))
                                    except:
                                        finished_value = 0
                            
                            all_models[model_str][part_name] = finished_value
                
            except Exception as e:
                print(f"Error loading {part_name}: {e}")
                inventory[part_name] = 0
        
        # 確保順序：工作台、底座、橫樑、立柱
        inventory = {
            '工作台': inventory.get('工作台', 0),
            '底座': inventory.get('底座', 0),
            '橫樑': inventory.get('橫樑', 0),
            '立柱': inventory.get('立柱', 0)
        }
        
        
        # 轉換機型數據為列表，只保留有庫存的機型
        details = []
        for model_data in all_models.values():
            if any(model_data[part] > 0 for part in ['工作台', '底座', '橫樑', '立柱']):
                details.append(model_data)
        
        return {'summary': inventory, 'details': details}
    except Exception as e:
        print(f"Error loading casting inventory: {e}")
        return {'summary': {}, 'details': [], 'error': str(e)}

# 欄位配置 (全域，供多個函式使用)
CONFIGS = {
    '底座': [('素材', 2), ('M4', 3), ('M3', 4), ('成品研磨', 5), ('總數', 7)],
    '工作台': [('素材', 2), ('W1', 3), ('W2', 4), ('W3', 5), ('W4', 6), ('成品', 7), ('總數', 9)],
    '橫樑': [('素材', 2), ('M6', 4), ('M5', 5), ('成品研磨', 6), ('總數', 8)],
    '立柱': [('素材', 2), ('半品', 3), ('成品銑工', 4), ('成品研磨', 5), ('總數', 6)]
}

SHEET_MAP = {'底座': 1, '工作台': 2, '橫樑': 3, '立柱': 4}

def get_part_details(part_type):
    """載入特定鑄件的詳細製程資料 (動態表頭)"""
    try:
        casting_file = current_app.config['CASTING_FILE']
        sheet_idx = SHEET_MAP.get(part_type)
        if sheet_idx is None: return {"headers": [], "rows": []}

        config = CONFIGS.get(part_type, [])
        headers = ['品號', '機型'] + [c[0] for c in config]
        
        df = pd.read_excel(casting_file, sheet_name=sheet_idx)
        
        rows = []
        for _, row in df.iterrows():
            if pd.isna(row.iloc[0]) and pd.isna(row.iloc[1]): continue
            
            def to_int(val):
                try: return int(float(val)) if pd.notna(val) else 0
                except: return 0

            # 建立資料列
            data_row = {
                '品號': str(row.iloc[0]),
                '機型': str(row.iloc[1])
            }
            # 動態加入各階段數據
            has_data = False
            for label, idx in config:
                val = to_int(row.iloc[idx])
                data_row[label] = val
                if val > 0: has_data = True
            
            if has_data:
                rows.append(data_row)
                
        return {"headers": headers, "rows": rows}
    except Exception as e:
        print(f"Error loading {part_type} details: {e}")
        return {"headers": [], "rows": []}

def update_cell(part_type, item_id, field, new_value, user_id):
    """更新 Excel 儲存格並記錄歷程"""
    try:
        casting_file = current_app.config['CASTING_FILE']
        sheet_idx = SHEET_MAP.get(part_type)
        config = CONFIGS.get(part_type, [])
        
        if sheet_idx is None:
            return {'success': False, 'error': '無效的鑄件類型'}
        
        # 找出欄位索引
        col_idx = None
        for label, idx in config:
            if label == field:
                col_idx = idx
                break
        
        if col_idx is None:
            return {'success': False, 'error': '無效的欄位'}
        
        # 使用 openpyxl 開啟並修改
        wb = load_workbook(casting_file)
        ws = wb.worksheets[sheet_idx]
        
        # 找出對應行 (品號在第一欄)
        target_row = None
        old_value = None
        for row_num in range(2, ws.max_row + 1):  # 跳過標題行
            cell_value = ws.cell(row=row_num, column=1).value
            if str(cell_value) == str(item_id):
                target_row = row_num
                old_value = ws.cell(row=row_num, column=col_idx + 1).value  # openpyxl 1-indexed
                break
        
        if target_row is None:
            return {'success': False, 'error': '找不到品號'}
        
        # 更新儲存格 (openpyxl column is 1-indexed)
        ws.cell(row=target_row, column=col_idx + 1, value=new_value)
        
        # 計算並更新總數 (不含總數欄本身)
        total = 0
        for label, idx in config:
            if label != '總數':
                cell_val = ws.cell(row=target_row, column=idx + 1).value
                total += int(cell_val) if cell_val else 0
        
        # 找出總數欄索引
        total_col_idx = None
        for label, idx in config:
            if label == '總數':
                total_col_idx = idx
                break
        
        if total_col_idx:
            ws.cell(row=target_row, column=total_col_idx + 1, value=total)
        
        wb.save(casting_file)
        wb.close()
        
        # 記錄歷程
        log_edit(part_type, item_id, field, old_value, new_value, user_id)
        
        return {'success': True, 'old_value': old_value, 'total': total}
    
    except Exception as e:
        print(f"Error updating cell: {e}")
        return {'success': False, 'error': str(e)}

def log_edit(part_type, item_id, field, old_value, new_value, user_id):
    """記錄編輯歷程"""
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'edit_history.json')
        
        history = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.insert(0, {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user': user_id,
            'part': part_type,
            'item_id': item_id,
            'field': field,
            'old_value': old_value,
            'new_value': new_value
        })
        
        # 只保留最近 500 筆
        history = history[:500]
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    except Exception as e:
        print(f"Error logging edit: {e}")

def get_edit_history(part_type, limit=50):
    """取得特定鑄件的修改歷程"""
    try:
        log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs', 'edit_history.json')
        
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 過濾該鑄件的歷程
        filtered = [h for h in history if h.get('part') == part_type]
        return filtered[:limit]
    
    except Exception as e:
        print(f"Error reading history: {e}")
        return []

def get_item_history(part_type, item_id, limit=100):
    """取得特定品號的完整修改歷程"""
    try:
        log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs', 'edit_history.json')
        
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 過濾該品號的歷程
        filtered = [h for h in history if h.get('part') == part_type and h.get('item_id') == item_id]
        return filtered[:limit]
    
    except Exception as e:
        print(f"Error reading item history: {e}")
        return []

def get_history_stats(part_type):
    """取得歷程統計資訊"""
    try:
        log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs', 'edit_history.json')
        
        if not os.path.exists(log_file):
            return {'total_edits': 0, 'unique_items': 0, 'recent_activity': []}
        
        with open(log_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 過濾該鑄件的歷程
        filtered = [h for h in history if h.get('part') == part_type]
        
        # 統計資訊
        unique_items = set(h.get('item_id') for h in filtered)
        unique_users = set(h.get('user') for h in filtered)
        
        # 最近活動（最近7天）
        from datetime import datetime, timedelta
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        recent = []
        for h in filtered[:20]:  # 最近20筆
            try:
                ts = datetime.strptime(h.get('timestamp', ''), '%Y-%m-%d %H:%M:%S')
                if ts >= week_ago:
                    recent.append(h)
            except:
                pass
        
        return {
            'total_edits': len(filtered),
            'unique_items': len(unique_items),
            'unique_users': len(unique_users),
            'recent_activity': recent
        }
    
    except Exception as e:
        print(f"Error getting history stats: {e}")
        return {'total_edits': 0, 'unique_items': 0, 'recent_activity': []}

import pandas as pd
from flask import current_app
from openpyxl import load_workbook
from datetime import datetime
import json
import os

def normalize_model_name(model_name):
    """標準化機型名稱，移除後綴變體"""
    import re
    if not model_name:
        return model_name
    
    normalized = str(model_name).strip()
    
    # 移除常見後綴（主底座、副底座、富底座）
    normalized = re.sub(r'(主底座|副底座|富底座)$', '', normalized)
    
    # 移除括號內容（如 (工作台-鑽孔)）
    normalized = re.sub(r'\([^)]*\)$', '', normalized)
    
    # 清理尾部的連字符、底線和空格
    normalized = re.sub(r'[-_\s]+$', '', normalized).strip()
    
    return normalized

def _get_master_model_list():
    """從所有零件工作表收集完整機型清單（保留原始名稱，智能分組排序）"""
    try:
        casting_file = current_app.config['CASTING_FILE']
        xl = pd.ExcelFile(casting_file)
        
        all_models = set()
        
        # 從四個零件分頁收集所有機型
        for sheet_name, sheet_idx in [('底座', 1), ('工作台', 2), ('橫樑', 3), ('立柱', 4)]:
            try:
                df = pd.read_excel(xl, sheet_name=sheet_idx)
                # 機型通常在第二欄（index 1）
                if len(df.columns) > 1:
                    model_col = df.columns[1]
                    models = df[model_col].dropna().unique()
                    for m in models:
                        model_str = str(m).strip()
                        if model_str and model_str != 'nan':
                            all_models.add(model_str)
            except Exception as e:
                print(f"Error reading {sheet_name}: {e}")
        
        # 智能排序：先按標準化名稱分組，再按原始名稱排序
        def sort_key(model_name):
            # 使用標準化名稱作為主排序鍵，原始名稱作為次排序鍵
            normalized = normalize_model_name(model_name)
            # 移除連字符進行比較，讓 HSA636 和 HSA-636 視為相同
            normalized_no_dash = normalized.replace('-', '').replace('_', '')
            return (normalized_no_dash, model_name)
        
        return sorted(list(all_models), key=sort_key)
    except Exception as e:
        print(f"Error loading master model list: {e}")
        return []

def load_casting_inventory():
    """載入鑄件庫存資料"""
    try:
        casting_file = current_app.config['CASTING_FILE']
        xl = pd.ExcelFile(casting_file)
        
        # 從各個鑄件工作表計算總數
        inventory = {}
        all_models = {}  # 儲存所有機型的數據

        # 1. 建立完整機型清單（從所有零件分頁收集）
        master_models = _get_master_model_list()
        for model_str in master_models:
            all_models[model_str] = {'機型': model_str, '工作台': 0, '底座': 0, '橫樑': 0, '立柱': 0}
        
        for part_name, sheet_idx in [('底座', 1), ('工作台', 2), ('橫樑', 3), ('立柱', 4)]:
            try:
                df = pd.read_excel(xl, sheet_name=sheet_idx)
                
                # 取得成品欄位索引 (ByName logic)
                config = CONFIGS.get(part_name, [])
                finished_col_idx = None
                for label, idx in config:
                    if label in ['成品', '成品研磨']:
                        finished_col_idx = idx
                        break
                
                # 初始化該料件的總數
                part_total = 0

                # 提取機型詳細資料並累加總數
                if '機型' in df.columns:
                    for _, row in df.iterrows():
                        model = row.get('機型', '')
                        # 排除無效機型
                        if pd.notna(model) and str(model).strip() and str(model).strip() != '品號':
                            model_str = str(model).strip()
                            
                            # 初始化該機型的數據
                            if model_str not in all_models:
                                all_models[model_str] = {'機型': model_str, '工作台': 0, '底座': 0, '橫樑': 0, '立柱': 0}
                            
                            # 取得成品數量
                            finished_value = 0
                            if finished_col_idx is not None:
                                val = row.iloc[finished_col_idx]
                                if pd.notna(val):
                                    try:
                                        finished_value = int(float(val))
                                    except:
                                        finished_value = 0
                            
                            # 累加到總表 (使用 += 處理重複出現的機型)
                            all_models[model_str][part_name] += finished_value
                            
                            # 累加到該料件總數
                            part_total += finished_value
                
                # 設定該料件的總庫存
                inventory[part_name] = part_total
                
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
        
        
        # 轉換機型數據為列表 (包含零庫存機型)
        details = list(all_models.values())
        
        return {'summary': inventory, 'details': details, 'all_models': all_models}
    except Exception as e:
        print(f"Error loading casting inventory: {e}")
        return {'summary': {}, 'details': [], 'all_models': {}, 'error': str(e)}

def get_zero_inventory_models():
    """獲取總數為0的機型列表（庫存警示）"""
    try:
        casting_data = load_casting_inventory()
        all_models = casting_data.get('all_models', {})
        
        # 找出總數為0的機型
        zero_models = []
        for model_str, model_data in all_models.items():
            total = sum(model_data.get(part, 0) for part in ['工作台', '底座', '橫樑', '立柱'])
            if total == 0:
                zero_models.append({
                    '機型': model_str,
                    '工作台': model_data.get('工作台', 0),
                    '底座': model_data.get('底座', 0),
                    '橫樑': model_data.get('橫樑', 0),
                    '立柱': model_data.get('立柱', 0)
                })
        
        return zero_models
    except Exception as e:
        print(f"Error getting zero inventory models: {e}")
        return []


# 欄位配置 (全域，供多個函式使用)
CONFIGS = {
    '底座': [('素材', 2), ('M4', 3), ('M3', 4), ('成品研磨', 5), ('總數', 7)],
    '工作台': [('素材', 2), ('W1', 3), ('W2', 4), ('W3', 5), ('W4', 6), ('成品', 7), ('總數', 9)],
    '橫樑': [('素材', 2), ('M6', 4), ('M5', 5), ('成品研磨', 6), ('總數', 8)],
    '立柱': [('素材', 2), ('半品', 3), ('成品銑工', 4), ('成品研磨', 5), ('總數', 6)]
}

SHEET_MAP = {'底座': 1, '工作台': 2, '橫樑': 3, '立柱': 4}

def get_part_details(part_type):
    """載入特定鑄件的詳細製程資料 (顯示所有原始機型名稱)"""
    try:
        casting_file = current_app.config['CASTING_FILE']
        sheet_idx = SHEET_MAP.get(part_type)
        if sheet_idx is None: return {"headers": [], "rows": []}

        config = CONFIGS.get(part_type, [])
        headers = ['品號', '機型'] + [c[0] for c in config]
        
        df = pd.read_excel(casting_file, sheet_name=sheet_idx)
        
        # 建立現有數據索引
        existing_rows = {}
        for _, row in df.iterrows():
            if pd.isna(row.iloc[0]) and pd.isna(row.iloc[1]): 
                continue
            model_name = str(row.iloc[1]).strip()
            existing_rows[model_name] = row

        # 取得完整機型清單（保留原始名稱）
        master_models = _get_master_model_list()
        
        def to_int(val):
            try: 
                return int(float(val)) if pd.notna(val) else 0
            except: 
                return 0
        
        rows = []
        for model_name in master_models:
            # 只顯示在 Excel 中有品號的機型
            if model_name in existing_rows:
                row = existing_rows[model_name]
                part_number = str(row.iloc[0])
                
                # 跳過品號為空或 N/A 的機型
                if part_number and part_number not in ['nan', 'N/A', '']:
                    data_row = {'機型': model_name, '品號': part_number}
                    for label, idx in config:
                        data_row[label] = to_int(row.iloc[idx])
                    rows.append(data_row)
            
        return {"headers": headers, "rows": rows}
    except Exception as e:
        print(f"Error loading {part_type} details: {e}")
        import traceback
        traceback.print_exc()
        return {"headers": [], "rows": []}


def update_cell(part_type, item_id, field, new_value, user_id, model_name=None):
    """更新 Excel 儲存格並記錄歷程 (支援依機型更新及自動新增列)"""
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
            return {'success': False, 'error': f'無效的欄位: {field}'}
        
        # 使用 openpyxl 開啟並修改
        wb = load_workbook(casting_file)
        ws = wb.worksheets[sheet_idx]
        
        # 找出對應行
        target_row = None
        old_value = None
        
        # 方式1: 依品號搜尋 (僅當 item_id 不是 'N/A' 時)
        if item_id and item_id != 'N/A':
            for row_num in range(2, ws.max_row + 1):
                cell_value = ws.cell(row=row_num, column=1).value
                if str(cell_value) == str(item_id):
                    target_row = row_num
                    break
        
        
        # 方式2: 依機型搜尋 (如果 item_id 找不到或為 'N/A')
        if target_row is None and model_name:
            for row_num in range(2, ws.max_row + 1):
                model_cell_value = ws.cell(row=row_num, column=2).value
                if model_cell_value and str(model_cell_value).strip() == str(model_name).strip():
                    target_row = row_num
                    # 同時更新 item_id 以便後續記錄
                    item_id = ws.cell(row=row_num, column=1).value or 'N/A'
                    break
        
        # 如果還是找不到，且有機型名稱，則新增一行
        if target_row is None and model_name:
            target_row = ws.max_row + 1
            ws.cell(row=target_row, column=1, value='N/A')  # 新增列品號設為 N/A
            ws.cell(row=target_row, column=2, value=model_name)
            item_id = 'N/A'
            print(f"[INFO] Appended new row for model: {model_name}")
        
        if target_row is None:
            return {'success': False, 'error': '找不到對應的品號或機型'}
        
        # 取得舊值
        old_value = ws.cell(row=target_row, column=col_idx + 1).value
        
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
        
        if total_col_idx is not None:
            ws.cell(row=target_row, column=total_col_idx + 1, value=total)
        
        wb.save(casting_file)
        wb.close()
        
        # 記錄歷程
        log_edit(part_type, str(item_id) if item_id else model_name, field, old_value, new_value, user_id)
        
        return {'success': True, 'old_value': old_value, 'total': total, 'item_id': item_id}
    
    except Exception as e:
        import traceback
        traceback.print_exc()
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

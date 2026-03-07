import pandas as pd
from flask import current_app
from openpyxl import load_workbook
from datetime import datetime
import json
import os
import glob

# 快取
_LIFTING_CACHE = {'mtime': 0, 'data': None}

def get_lifting_file_path():
    """尋找D槽中的吊具清冊"""
    # 這裡我們假設只有一個包含 '吊具清冊' 的 xlsx，或者直接指定
    files = glob.glob('D:\\app\\mes\\*吊具*.xlsx')
    if files:
        return files[0]
    return os.path.join(os.path.dirname(__file__), '..', '..', '吊具清冊.xlsx') # fallback

SHEET_NAMES = ['吊具', '吊鍊', '布帶']

def ensure_columns(df):
    """確保有借用人跟借用日期欄位"""
    if '目前借用人' not in df.columns:
        df['目前借用人'] = ''
    if '借用日期' not in df.columns:
        df['借用日期'] = ''
    return df

def load_lifting_inventory():
    """載入吊具清單"""
    file_path = get_lifting_file_path()
    if not os.path.exists(file_path):
        return {}

    current_mtime = os.path.getmtime(file_path)
    if _LIFTING_CACHE['mtime'] == current_mtime and _LIFTING_CACHE['data']:
        return _LIFTING_CACHE['data']

    try:
        xl = pd.ExcelFile(file_path)
        data = {}
        for sheet in SHEET_NAMES:
            if sheet in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet)
                df = df.fillna('')
                df = ensure_columns(df)
                
                # Convert DataFrame to list of dicts
                items = []
                for _, row in df.iterrows():
                    # 吊具編號是唯一識別
                    item_id = str(row.get('吊具編號', '')).strip()
                    if not item_id or item_id == 'nan':
                        continue
                        
                    items.append({
                        'category': sheet,
                        'id': item_id,
                        'spec': str(row.get('吊具規格 /重量/長度', '')),
                        'location': str(row.get('放置位置', '')),
                        'status': str(row.get('使用狀態', '')),
                        'borrower': str(row.get('目前借用人', '')),
                        'borrow_date': str(row.get('借用日期', ''))
                    })
                data[sheet] = items
                
        _LIFTING_CACHE['mtime'] = current_mtime
        _LIFTING_CACHE['data'] = data
        return data
    except Exception as e:
        print(f"Error loading lifting inventory: {e}")
        return {}

def update_lifting_status(category, item_id, action, user_name):
    """
    更新吊具狀態
    action: 'borrow' 或 'return'
    """
    file_path = get_lifting_file_path()
    if not os.path.exists(file_path):
        return False, "找不到吊具清冊檔案"

    try:
        wb = load_workbook(file_path)
        if category not in wb.sheetnames:
            return False, f"找不到工作表: {category}"

        ws = wb[category]
        headers = {cell.value: idx for idx, cell in enumerate(ws[1])}
        
        # 確保新的兩欄存在
        if '目前借用人' not in headers:
            new_col_idx = len(headers) + 1
            ws.cell(row=1, column=new_col_idx, value='目前借用人')
            headers['目前借用人'] = new_col_idx - 1
            
        if '借用日期' not in headers:
            new_col_idx = len(headers) + 1
            ws.cell(row=1, column=new_col_idx, value='借用日期')
            headers['借用日期'] = new_col_idx - 1

        if '吊具編號' not in headers or '使用狀態' not in headers:
            return False, "工作表缺少必要標題：'吊具編號' 或 '使用狀態'"

        id_col = headers['吊具編號']
        status_col = headers['使用狀態']
        borrower_col = headers['目前借用人']
        date_col = headers['借用日期']

        row_found = None
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if str(row[id_col]).strip() == str(item_id):
                row_found = row_idx
                break

        if not row_found:
            return False, f"找不到吊具編號: {item_id}"

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if action == 'borrow':
            ws.cell(row=row_found, column=status_col + 1, value='借用中')
            ws.cell(row=row_found, column=borrower_col + 1, value=user_name)
            ws.cell(row=row_found, column=date_col + 1, value=now_str)
        elif action == 'return':
            ws.cell(row=row_found, column=status_col + 1, value='在庫')
            ws.cell(row=row_found, column=borrower_col + 1, value='')
            ws.cell(row=row_found, column=date_col + 1, value='')
        else:
            return False, "未知的操作"

        wb.save(file_path)
        
        # 強制刷新快取
        _LIFTING_CACHE['mtime'] = 0 
        return True, "更新成功"

    except PermissionError:
        return False, "檔案可能被另一個程式(如 Excel)開啟中，請先關閉。"
    except Exception as e:
        print(f"Error updating lifting status: {e}")
        return False, str(e)

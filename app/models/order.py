import pandas as pd
from flask import current_app
from datetime import datetime

# 全域快取
PICKING_CACHE = None
PICKING_LAST_UPDATE = None

def clean_id(val):
    if pd.isna(val): return ""
    try:
        # 處理科學記號 e.g. 1.1e9 -> 1100000000
        return str(int(float(val))).strip()
    except:
        return str(val).strip()

def find_col(df, keywords):
    """根據關鍵字在 dataframe 欄位中尋找對應的欄位名"""
    for col in df.columns:
        col_str = str(col)
        if any(k in col_str for k in keywords):
            return col
    return None

def get_picking_data():
    """讀取成品撥料資料，回傳以訂單為 Key 的需求資料 (含快取)"""
    global PICKING_CACHE, PICKING_LAST_UPDATE
    
    if PICKING_CACHE is not None:
        return PICKING_CACHE
        
    try:
        picking_file = current_app.config['PICKING_FILE']
        print(f"Loading Picking Data from {picking_file}...")
        # 讀取撥料單 (Excel 常態無亂碼)
        df = pd.read_excel(picking_file, usecols=[0, 1, 4, 5, 8])
        df.columns = ['訂單', '物料', '未結數量', '物料說明', '需求日期']
        
        picking_map = {}
        for _, row in df.iterrows():
            order_id = clean_id(row['訂單'])
            if not order_id: continue
                
            qty = row['未結數量']
            if pd.isna(qty) or qty <= 0: continue
                
            item_name = str(row['物料說明'])
            need_date = row['需求日期']
            
            if order_id not in picking_map:
                picking_map[order_id] = {'底座': 0, '工作台': 0, '橫樑': 0, '立柱': 0, 'dates': []}
            
            if '底座' in item_name and '馬達' not in item_name:
                picking_map[order_id]['底座'] += qty
            elif '工作台' in item_name:
                picking_map[order_id]['工作台'] += qty
            elif '橫樑' in item_name:
                picking_map[order_id]['橫樑'] += qty
            elif '立柱' in item_name:
                picking_map[order_id]['立柱'] += qty
                
            if pd.notna(need_date):
                picking_map[order_id]['dates'].append(need_date)
        
        PICKING_CACHE = picking_map
        PICKING_LAST_UPDATE = datetime.now()
        return picking_map
    except Exception as e:
        print(f"Error loading picking data: {e}")
        return {}

def load_orders():
    """載入工單總表資料並整合撥料需求 (整合多分頁並解決亂碼)"""
    try:
        picking_data = get_picking_data()
        workorder_file = current_app.config['WORKORDER_FILE']
        
        xl = pd.ExcelFile(workorder_file)
        all_parsed_orders = []
        seen_work_orders = set()
        
        # 關鍵字清單 (包含亂碼可能的樣子)
        KW_WO = ["工單", "號碼", "u", "W", "序號", "編號", "u"]
        KW_ORDER = ["訂單", "q", "q"]
        KW_CUST = ["客戶", "U", "U"]
        KW_DESC = ["品號", "說明", "~", "~"]
        KW_START = ["開始", "Ͳ", "Ͳ"]
        KW_END = ["結束", "Term", "Ͳ"]

        for i, sheet_name in enumerate(xl.sheet_names):
            if i == 1: continue # 排除半品
            
            df = pd.read_excel(xl, sheet_name=sheet_name)
            
            # 定位欄位
            col_wo = find_col(df, KW_WO)
            col_order = find_col(df, KW_ORDER)
            col_cust = find_col(df, KW_CUST)
            col_desc = find_col(df, KW_DESC)
            col_start = find_col(df, KW_START)
            col_end = find_col(df, KW_END)
            
            if col_start and col_start == col_end:
                for c in df.columns:
                    if c != col_start and any(k in str(c) for k in ["結束", "Term"]):
                        col_end = c; break

            for _, row in df.iterrows():
                try:
                    wo_val = row.get(col_wo) if col_wo else None
                    order_val = row.get(col_order) if col_order else None
                    
                    wo_str = clean_id(wo_val)
                    order_str = clean_id(order_val)
                    
                    if not wo_str and not order_str: continue
                    
                    # 用戶要求：僅保留 10000 開頭的工單
                    if not wo_str.startswith("10000"): continue
                    
                    # 建立唯一識別碼
                    id_key = wo_str
                    if id_key in seen_work_orders: continue
                    seen_work_orders.add(id_key)

                    needs = {'底座': 0, '工作台': 0, '橫樑': 0, '立柱': 0}
                    picking_dates = []
                    if order_str and order_str in picking_data:
                        picked = picking_data[order_str]
                        needs.update({k: int(v) for k, v in picked.items() if k != 'dates'})
                        picking_dates = picked['dates']
                    
                    def safe_date_str(val):
                        if pd.isna(val) or str(val).strip() == "": return ""
                        try:
                            if isinstance(val, (datetime, pd.Timestamp)): return val.strftime('%Y-%m-%d')
                            return str(val).split(' ')[0]
                        except: return ""

                    need_date_display = ""
                    if picking_dates:
                        try: need_date_display = min(picking_dates).strftime('%Y-%m-%d')
                        except: pass

                    all_parsed_orders.append({
                        '工單': wo_str if wo_str else "-",
                        '訂單': order_str,
                        '客戶': str(row.get(col_cust))[:20] if col_cust and pd.notna(row.get(col_cust)) else "",
                        '品號說明': str(row.get(col_desc)) if col_desc and pd.notna(row.get(col_desc)) else "",
                        '生產開始': safe_date_str(row.get(col_start)) if col_start else "",
                        '生產結束': safe_date_str(row.get(col_end)) if col_end else "",
                        '需求日期': need_date_display,
                        '需求_底座': needs['底座'],
                        '需求_工作台': needs['工作台'],
                        '需求_橫樑': needs['橫樑'],
                        '需求_立柱': needs['立柱']
                    })
                except: continue

        # 排序：進行中優先 (權重 0)，已完成在後 (權重 1)，並依結束日期排序
        today_str = datetime.now().strftime('%Y-%m-%d')
        def get_sort_weight(o):
            is_active = o['生產結束'] >= today_str if o['生產結束'] else False
            # 進行中為 0, 已完成為 1
            status_weight = 0 if is_active else 1
            # 日期排序：
            # 進行中：日期越近(小)越前
            # 已完成：日期越遠(大)越前 (可選)
            date_val = o['生產結束'] if o['生產結束'] else '9999-12-31'
            return (status_weight, date_val)

        all_parsed_orders.sort(key=get_sort_weight)

        total_demand = {'底座': 0, '工作台': 0, '橫樑': 0, '立柱': 0}
        for o in all_parsed_orders:
            total_demand['底座'] += o['需求_底座']
            total_demand['工作台'] += o['需求_工作台']
            total_demand['橫樑'] += o['需求_橫樑']
            total_demand['立柱'] += o['需求_立柱']

        in_progress = sum(1 for o in all_parsed_orders if o['生產結束'] and o['生產結束'] >= today_str)
        
        return {
            'orders': all_parsed_orders,
            'stats': {'total': len(all_parsed_orders), 'completed': len(all_parsed_orders) - in_progress, 'in_progress': in_progress},
            'demand': total_demand
        }
    except Exception as e:
        print(f"Error loading all orders: {e}")
        return {'orders': [], 'stats': {}, 'demand': {}}

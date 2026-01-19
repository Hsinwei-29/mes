import pandas as pd
from flask import current_app
from datetime import datetime

# 全域快取
PICKING_CACHE = None
PICKING_LAST_UPDATE = None

def get_picking_data():
    """讀取成品撥料資料，回傳以訂單為 Key 的需求資料 (含快取)"""
    global PICKING_CACHE, PICKING_LAST_UPDATE
    
    # 如果已有快取，直接回傳
    if PICKING_CACHE is not None:
        return PICKING_CACHE
        
    try:
        picking_file = current_app.config['PICKING_FILE']
        print(f"Loading Picking Data from {picking_file}...")
        df = pd.read_excel(picking_file, usecols=[0, 1, 4, 5, 8])
        df.columns = ['訂單', '物料', '未結數量', '物料說明', '需求日期']
        
        picking_map = {}
        for _, row in df.iterrows():
            order_id = str(row['訂單']).strip()
            if not order_id or order_id == 'nan': continue
                
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
        
        print(f"Picking Data Loaded. {len(picking_map)} orders found.")
        PICKING_CACHE = picking_map
        PICKING_LAST_UPDATE = datetime.now()
        return picking_map
    except Exception as e:
        print(f"Error loading picking data: {e}")
        return {}

def load_orders():
    """載入工單總表資料並整合撥料需求"""
    try:
        picking_data = get_picking_data()
        workorder_file = current_app.config['WORKORDER_FILE']
        df = pd.read_excel(workorder_file, sheet_name='工單總表')
        
        orders = []
        total_demand = {'底座': 0, '工作台': 0, '橫樑': 0, '立柱': 0}
        
        for _, row in df.iterrows():
            try:
                work_order = row.get('工單號碼')
                if pd.isna(work_order): continue
                
                work_order_str = str(int(float(work_order)))
                order_num_raw = row.get('訂單號碼')
                order_num_str = ''
                if pd.notna(order_num_raw):
                    try: order_num_str = str(int(float(order_num_raw)))
                    except: order_num_str = str(order_num_raw)
                
                def safe_date(val):
                    if pd.isna(val): return ''
                    try: return val.strftime('%Y-%m-%d')
                    except: return str(val)
                
                needs = {'底座': 0, '工作台': 0, '橫樑': 0, '立柱': 0}
                picking_dates = []
                
                if order_num_str and order_num_str in picking_data:
                    data = picking_data[order_num_str]
                    needs['底座'] = int(data['底座'])
                    needs['工作台'] = int(data['工作台'])
                    needs['橫樑'] = int(data['橫樑'])
                    needs['立柱'] = int(data['立柱'])
                    picking_dates = data['dates']
                
                need_date_display = ''
                if picking_dates:
                    try: need_date_display = min(picking_dates).strftime('%Y-%m-%d')
                    except: pass
                
                total_demand['底座'] += needs['底座']
                total_demand['工作台'] += needs['工作台']
                total_demand['橫樑'] += needs['橫樑']
                total_demand['立柱'] += needs['立柱']

                orders.append({
                    '工單': work_order_str,
                    '訂單': order_num_str,
                    '客戶': str(row.get('下單客戶名稱', '')) if pd.notna(row.get('下單客戶名稱')) else '',
                    '品號說明': str(row.get('品號說明', '')) if pd.notna(row.get('品號說明')) else '',
                    '生產開始': safe_date(row.get('生產開始')),
                    '生產結束': safe_date(row.get('生產結束')),
                    '需求日期': need_date_display,
                    '需求_底座': needs['底座'],
                    '需求_工作台': needs['工作台'],
                    '需求_橫樑': needs['橫樑'],
                    '需求_立柱': needs['立柱']
                })
            except: continue
        
        today = datetime.now()
        in_progress = sum(1 for o in orders if o['生產結束'] and datetime.strptime(o['生產結束'], '%Y-%m-%d') >= today)
        
        return {
            'orders': orders,
            'stats': {'total': len(orders), 'completed': len(orders) - in_progress, 'in_progress': in_progress},
            'demand': total_demand
        }
    except Exception as e:
        print(f"Error loading orders: {e}")
        return {'orders': [], 'stats': {}, 'demand': {}}

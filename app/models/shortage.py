"""
缺料分析模型
整合工單、成品撥料、鑄件盤點資料，計算缺料狀況
以工單號碼為主鍵連結資料
"""
import pandas as pd
from flask import current_app
from datetime import datetime
import os

# 缺料分析結果快取
SHORTAGE_CACHE = {
    'mtimes': (0, 0, 0),  # (casting_mtime, workorder_mtime, picking_mtime)
    'data': None
}

def is_casting_part(part_description):
    """判斷物料說明是否為鑄件零件
    
    Args:
        part_description: 物料說明文字
        
    Returns:
        tuple: (是否為鑄件, 零件類型或None)
    """
    if not part_description or pd.isna(part_description):
        return False, None
    
    desc = str(part_description).strip()
    
    # 檢查是否包含鑄件關鍵字
    casting_keywords = {
        '工作台': '工作台',
        '底座': '底座',
        '橫樑': '橫樑',
        '立柱': '立柱'
    }
    
    for keyword, part_type in casting_keywords.items():
        if keyword in desc:
            return True, part_type
    
    return False, None

def get_workorder_picking_mapping(casting_inventory=None):
    """從工單總表和成品撥料建立對應關係（重用 order.py 快取，避免重複讀取 Excel）"""
    try:
        if casting_inventory is None:
            casting_inventory = get_casting_inventory()

        # ── 1. 工單基本資訊（.xls 自動判斷 engine）────────────────────
        workorder_file = current_app.config['WORKORDER_FILE']
        wo_df = pd.read_excel(workorder_file, sheet_name=0)

        workorder_map = {}
        for _, row in wo_df.iterrows():
            wo_number = str(row['工單號碼']).strip() if pd.notna(row['工單號碼']) else None
            if not wo_number or wo_number in ['nan', 'N/A', '']:
                continue
            special_note = str(row.get('特規備註', '')).strip() if pd.notna(row.get('特規備註', '')) else ''
            woc = ''
            if '工單編碼' in row.index and pd.notna(row.get('工單編碼')):
                woc = str(row['工單編碼']).strip()
            elif '物料品號' in row.index and pd.notna(row.get('物料品號')):
                woc = str(row['物料品號']).strip()
            workorder_map[wo_number] = {
                '客戶名稱': str(row['下單客戶名稱']).strip() if pd.notna(row['下單客戶名稱']) else '',
                '生產開始': row['生產開始'] if pd.notna(row['生產開始']) else None,
                '生產結束': row['生產結束'] if pd.notna(row['生產結束']) else None,
                '工單編碼': woc,
                '特規備註': special_note,
                '零件需求': {}
            }

        # ── 2. 撥料資料：呼叫 get_picking_data() 確保快取已填充 ──────
        from ..models.order import PICKING_CACHE, get_picking_data
        picking_file = current_app.config['PICKING_FILE']

        # 先確保 PICKING_CACHE 已被填充（無論是否已初始化）
        get_picking_data()
        raw_df = PICKING_CACHE.get('raw_df')
        if raw_df is None:
            raw_df = pd.read_excel(picking_file, engine='openpyxl')

        # ── 3. 比對 ───────────────────────────────────────────────────
        for _, row in raw_df.iterrows():
            order_number = str(row['訂單']).strip() if pd.notna(row['訂單']) else None
            part_number_full = str(row['物料']).strip() if pd.notna(row['物料']) else None
            part_desc = str(row['物料說明']).strip() if pd.notna(row['物料說明']) else ''

            if not order_number or not part_number_full:
                continue

            part_number_base = part_number_full[:10] if len(part_number_full) >= 10 else part_number_full
            if part_number_base not in casting_inventory:
                continue

            part_type = casting_inventory[part_number_base]['零件類型']
            if order_number not in workorder_map:
                continue

            demand_qty = int(float(row['需求數量 (EINHEIT)'])) if pd.notna(row['需求數量 (EINHEIT)']) else 0
            picked_qty = int(float(row['領料數量 (EINHEIT)'])) if pd.notna(row['領料數量 (EINHEIT)']) else 0
            pending_qty = int(float(row['未結數量 (EINHEIT)'])) if pd.notna(row['未結數量 (EINHEIT)']) else 0

            if part_number_base in workorder_map[order_number]['零件需求']:
                workorder_map[order_number]['零件需求'][part_number_base]['需求數量'] += demand_qty
                workorder_map[order_number]['零件需求'][part_number_base]['已領料'] += picked_qty
                workorder_map[order_number]['零件需求'][part_number_base]['未結數量'] += pending_qty
            else:
                workorder_map[order_number]['零件需求'][part_number_base] = {
                    '需求數量': demand_qty,
                    '已領料': picked_qty,
                    '未結數量': pending_qty,
                    '物料說明': part_desc,
                    '零件類型': part_type
                }

        return workorder_map

    except Exception as e:
        print(f"Error building workorder-picking mapping: {e}")
        import traceback
        traceback.print_exc()
        return {}

def get_casting_inventory():
    """從 inventory.py 的快取資料建立鑄件盤點（避免重複讀取 Excel）

    Returns:
        dict: {品號: {'機型': str, '零件類型': str, '庫存': int, '在製品': int}}
    """
    try:
        from ..models.inventory import get_part_details, SHEET_MAP

        finished_key = {
            '底座': '成品研磨',
            '工作台': '成品',
            '橫樑': '成品研磨',
            '立柱': '成品研磨'
        }
        semi_keys = {
            '底座': ['素材', 'M4', 'M3'],
            '工作台': ['素材', 'W1', 'W2', 'W3', 'W4'],
            '橫樑': ['素材', 'M6', 'M5'],
            '立柱': ['素材', '半品', '成品銑工']
        }

        inventory = {}
        for part_type in SHEET_MAP:
            detail = get_part_details(part_type)  # 使用已快取的資料
            fin_key = finished_key.get(part_type, '成品')
            semi_key_list = semi_keys.get(part_type, [])

            for row in detail.get('rows', []):
                part_number = str(row.get('品號', '')).strip()
                if not part_number or part_number in ['nan', 'N/A', '']:
                    continue
                stock_val = row.get(fin_key, 0) or 0
                semi_val = sum(row.get(k, 0) or 0 for k in semi_key_list)
                material_val = row.get('素材', 0) or 0  # 素材單獨記錄
                inventory[part_number] = {
                    '機型': row.get('機型', ''),
                    '零件類型': part_type,
                    '庫存': int(stock_val),
                    '在製品': int(semi_val),
                    '素材': int(material_val)
                }

        return inventory
    except Exception as e:
        print(f"Error loading casting inventory (fast path): {e}")
        import traceback
        traceback.print_exc()
        return {}

def calculate_shortage():
    """計算缺料清單（以工單號碼為主鍵）
    
    Returns:
        list: [{
            '工單號碼': str,
            '客戶名稱': str,
            '生產開始': date,
            '生產結束': date,
            '品號': str,
            '物料說明': str,
            '零件類型': str,
            '需求數量': int,
            '已領料': int,
            '現有庫存': int,
            '缺料數量': int,
            '狀態': str
        }]
    """
    try:
        # 0. 檢查快取
        casting_file = current_app.config['CASTING_FILE']
        workorder_file = current_app.config['WORKORDER_FILE']
        picking_file = current_app.config['PICKING_FILE']
        
        current_mtimes = (0, 0, 0)
        try:
            current_mtimes = (
                os.path.getmtime(casting_file),
                os.path.getmtime(workorder_file),
                os.path.getmtime(picking_file)
            )
            
            # 如果快取存在且有資料且檔案未修改，直接回傳
            # 注意：空 list 不回傳快取，避免啟動競爭條件導致永久快取空結果
            global SHORTAGE_CACHE
            if (SHORTAGE_CACHE['data'] is not None and 
                len(SHORTAGE_CACHE['data']) > 0 and
                SHORTAGE_CACHE['mtimes'] == current_mtimes):
                print("Returning cached shortage data")
                return SHORTAGE_CACHE['data']
        except Exception as e:
            print(f"Error checking mtimes: {e}")

        # 1. 先獲取鑄件庫存（作為品號過濾依據）
        casting_inventory = get_casting_inventory()
        
        # 2. 獲取工單-撥料對應關係（只包含鑄件盤點中的品號）
        workorder_map = get_workorder_picking_mapping(casting_inventory)
        
        print(f"鑄件庫存: {len(casting_inventory)} 個品號")
        print(f"工單數量: {len(workorder_map)} 筆")
        
        # 3. 計算缺料
        shortage_list = []
        
        for wo_number, wo_data in workorder_map.items():
            customer = wo_data['客戶名稱']
            start_date = wo_data['生產開始']
            end_date = wo_data['生產結束']
            work_order_code = wo_data.get('工單編碼', '')
            special_note = wo_data.get('特規備註', '')
            
            # 遍歷該工單的所有零件需求
            for part_number, part_data in wo_data['零件需求'].items():
                demand_qty = part_data['需求數量']
                picked_qty = part_data['已領料']
                part_desc = part_data['物料說明']
                part_type = part_data['零件類型']
                
                # 從鑄件庫存取得現有庫存、在製品與素材
                current_stock = 0
                current_semi = 0
                current_material = 0
                if part_number in casting_inventory:
                    current_stock = casting_inventory[part_number]['庫存']
                    current_semi = casting_inventory[part_number].get('在製品', 0)
                    current_material = casting_inventory[part_number].get('素材', 0)
                
                # 計算目前缺料：需求數量 - 已領料（未考慮庫存）
                current_shortage = demand_qty - picked_qty
                
                # 計算最終缺料：需求數量 - 已領料 - 現有庫存
                final_shortage = demand_qty - picked_qty - current_stock
                
                # 記錄所有有需求的項目
                if demand_qty > 0:
                    shortage_list.append({
                        '工單號碼': wo_number,
                        '工單編碼': work_order_code,
                        '客戶名稱': customer,
                        '生產開始': start_date,
                        '生產結束': end_date,
                        '品號': part_number,
                        '物料說明': part_desc,
                        '零件類型': part_type,
                        '需求數量': demand_qty,
                        '已領料': picked_qty,
                        '目前缺料': current_shortage if current_shortage > 0 else 0,
                        '現有庫存': current_stock,
                        '現有在製品': current_semi,
                        '現有素材': current_material,  # 素材數量，用於判斷是否為嚴重缺料
                        '缺料數量': final_shortage if final_shortage > 0 else 0,
                        '特規備註': special_note,
                        '狀態': '已領足' if picked_qty >= demand_qty else ('庫存足' if final_shortage <= 0 else '缺料')
                    })
        
        # 按生產開始日期升序（最早優先）、缺料數量降序、工單號碼升序排序
        # 注意：有些生產開始可能是 NaT/None，需要處理
        def sort_key(x):
            date_val = x['生產開始']
            # 如果日期是 None 或 NaT，排在最後面 (或最前面，視需求而定，這裡假設有日期的優先)
            # 為了讓有日期的排前面並按時間排序，我們給 None 一個很大的日期
            if pd.isna(date_val):
                date_val = pd.Timestamp.max
            
            return (date_val, -x['缺料數量'], x['工單號碼'])

        shortage_list.sort(key=sort_key)
        
        print(f"缺料分析完成: 共 {len(shortage_list)} 筆記錄")
        print(f"缺料項目: {len([x for x in shortage_list if x['缺料數量'] > 0])} 筆")
        
        # 更新快取
        SHORTAGE_CACHE['mtimes'] = current_mtimes
        SHORTAGE_CACHE['data'] = shortage_list
        
        return shortage_list
    
    except Exception as e:
        print(f"Error calculating shortage: {e}")
        import traceback
        traceback.print_exc()
        return []

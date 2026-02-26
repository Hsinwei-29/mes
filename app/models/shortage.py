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
    """從工單總表和成品撥料建立對應關係（只包含鑄件盤點中存在的品號）
    
    Args:
        casting_inventory: 鑄件庫存字典，如果為 None 則自動載入
    
    Returns:
        dict: {
            工單號碼: {
                '客戶名稱': str,
                '生產開始': date,
                '生產結束': date,
                '零件需求': {
                    品號: {
                        '需求數量': int,
                        '已領料': int,
                        '未結數量': int,
                        '物料說明': str,
                        '零件類型': str
                    }
                }
            }
        }
    """
    try:
        # 如果沒有提供庫存資料，則載入
        if casting_inventory is None:
            casting_inventory = get_casting_inventory()

        # 1. 讀取工單總表（直接讀 Excel 第 0 sheet，不經過 order.py 快取）
        workorder_file = current_app.config['WORKORDER_FILE']
        wo_df = pd.read_excel(workorder_file, sheet_name=0)

        # 2. 讀取成品撥料資料
        picking_file = current_app.config['PICKING_FILE']
        pick_df = pd.read_excel(picking_file, sheet_name=0)
        
        # 3. 建立工單對應表
        workorder_map = {}
        
        # 從工單總表建立基本資訊
        for _, row in wo_df.iterrows():
            wo_number = str(row['工單號碼']).strip() if pd.notna(row['工單號碼']) else None
            
            if wo_number and wo_number not in ['nan', 'N/A', '']:
                # 提取特規備註（如果欄位存在）
                special_note = ''
                if '特規備註' in row.index and pd.notna(row['特規備註']):
                    special_note = str(row['特規備註']).strip()
                
                # 提取工單編碼（如果欄位存在，否則使用物料品號）
                work_order_code = ''
                if '工單編碼' in row.index and pd.notna(row['工單編碼']):
                    work_order_code = str(row['工單編碼']).strip()
                elif '物料品號' in row.index and pd.notna(row['物料品號']):
                    work_order_code = str(row['物料品號']).strip()
                
                workorder_map[wo_number] = {
                    '客戶名稱': str(row['下單客戶名稱']).strip() if pd.notna(row['下單客戶名稱']) else '',
                    '生產開始': row['生產開始'] if pd.notna(row['生產開始']) else None,
                    '生產結束': row['生產結束'] if pd.notna(row['生產結束']) else None,
                    '工單編碼': work_order_code,
                    '特規備註': special_note,
                    '零件需求': {}
                }
        
        # 4. 從成品撥料資料提取零件需求（只包含鑄件盤點中存在的品號）
        for _, row in pick_df.iterrows():
            order_number = str(row['訂單']).strip() if pd.notna(row['訂單']) else None
            part_number_full = str(row['物料']).strip() if pd.notna(row['物料']) else None
            part_desc = str(row['物料說明']).strip() if pd.notna(row['物料說明']) else ''
            
            if not order_number or not part_number_full:
                continue
            
            # ⭐ 關鍵修改：使用前10位數匹配品號（鑄件盤點是10位，成品撥料是12位含版本號）
            part_number_base = part_number_full[:10] if len(part_number_full) >= 10 else part_number_full
            
            # 檢查基礎品號是否在鑄件盤點中
            if part_number_base not in casting_inventory:
                continue
            
            # 從鑄件庫存中取得零件類型
            part_type = casting_inventory[part_number_base]['零件類型']
            
            # 如果工單號碼存在於工單總表中
            if order_number in workorder_map:
                # 提取數量資訊
                demand_qty = int(float(row['需求數量 (EINHEIT)'])) if pd.notna(row['需求數量 (EINHEIT)']) else 0
                picked_qty = int(float(row['領料數量 (EINHEIT)'])) if pd.notna(row['領料數量 (EINHEIT)']) else 0
                pending_qty = int(float(row['未結數量 (EINHEIT)'])) if pd.notna(row['未結數量 (EINHEIT)']) else 0
                
                # 使用基礎品號（10位）作為鍵
                # 如果該品號已存在，累加數量
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
    """從鑄件盤點提取現有庫存及在製品（直接使用 inventory.py 快取，避免重複讀取 Excel）

    Returns:
        dict: {品號: {'機型': str, '零件類型': str, '庫存': int, '在製品': int}}
    """
    try:
        from ..models.inventory import load_casting_inventory as _load_inv

        # 各零件成品欄映射
        finished_fields = {
            '底座': '成品研磨',
            '工作台': '成品',
            '橫樑': '成品研磨',
            '立柱': '成品研磨'
        }

        # 各零件半成品欄映射
        semi_finished_fields = {
            '底座': ['素材', 'M4', 'M3'],
            '工作台': ['素材', 'W1', 'W2', 'W3', 'W4'],
            '橫樑': ['素材', 'M6', 'M5'],
            '立柱': ['素材', '半品', '成品銑工']
        }

        from ..models.inventory import CONFIGS, SHEET_MAP
        import pandas as pd

        casting_file = current_app.config['CASTING_FILE']
        xl = pd.ExcelFile(casting_file)

        inventory = {}
        for part_type, sheet_idx in SHEET_MAP.items():
            df = pd.read_excel(xl, sheet_name=sheet_idx)
            config = CONFIGS.get(part_type, [])
            finished_label = finished_fields.get(part_type, '成品')
            finished_col_idx = next(
                (idx for label, idx in config if label == finished_label), None
            )
            
            semi_labels = semi_finished_fields.get(part_type, [])
            semi_col_indices = [idx for label, idx in config if label in semi_labels]

            for _, row in df.iterrows():
                part_number = str(row.iloc[0]).strip()
                model_name = str(row.iloc[1]).strip()

                if part_number and part_number not in ['nan', 'N/A', '']:
                    try:
                        stock_val = 0
                        if finished_col_idx is not None:
                            val = row.iloc[finished_col_idx]
                            stock_val = int(float(val)) if pd.notna(val) else 0

                        semi_val = 0
                        for idx in semi_col_indices:
                            s_val = row.iloc[idx]
                            semi_val += int(float(s_val)) if pd.notna(s_val) else 0

                        inventory[part_number] = {
                            '機型': model_name,
                            '零件類型': part_type,
                            '庫存': stock_val,
                            '在製品': semi_val
                        }
                    except:
                        continue

        return inventory
    except Exception as e:
        print(f"Error loading casting inventory: {e}")
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
            
            # 如果快取存在且檔案未修改，直接回傳
            global SHORTAGE_CACHE
            if (SHORTAGE_CACHE['data'] is not None and 
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
                
                # 從鑄件庫存取得現有庫存與在製品
                current_stock = 0
                current_semi = 0
                if part_number in casting_inventory:
                    current_stock = casting_inventory[part_number]['庫存']
                    current_semi = casting_inventory[part_number].get('在製品', 0)
                
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

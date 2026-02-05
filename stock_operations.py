
def stock_in_material(part_name, quantity):
    """
    入庫操作 - 增加素材數量
    
    Args:
        part_name: 零件名稱 (工作台/底座/橫樑/立柱)
        quantity: 入庫數量
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        from flask import current_app
        import pandas as pd
        import os
        
        casting_file = current_app.config['CASTING_FILE']
        
        # 零件對應的工作表索引
        sheet_mapping = {
            '底座': 1,
            '工作台': 2,
            '橫樑': 3,
            '立柱': 4
        }
        
        if part_name not in sheet_mapping:
            return {'success': False, 'error': f'未知的零件名稱: {part_name}'}
        
        sheet_idx = sheet_mapping[part_name]
        
        # 讀取 Excel 檔案
        xl = pd.ExcelFile(casting_file)
        df = pd.read_excel(xl, sheet_name=sheet_idx)
        
        # 取得素材欄位索引 (所有零件的素材都在索引 2)
        material_col_idx = 2
        
        # 計算當前素材總數
        current_total = 0
        for _, row in df.iterrows():
            model = row.get('機型', '')
            if pd.notna(model) and str(model).strip() and str(model).strip() != '品號':
                val = row.iloc[material_col_idx]
                if pd.notna(val):
                    try:
                        current_total += int(float(val))
                    except:
                        pass
        
        # 將新數量分配到第一個有效機型的素材欄位
        # (實際應用中可能需要更複雜的邏輯)
        updated = False
        for idx, row in df.iterrows():
            model = row.get('機型', '')
            if pd.notna(model) and str(model).strip() and str(model).strip() != '品號':
                # 找到第一個有效機型，增加素材數量
                current_val = row.iloc[material_col_idx]
                new_val = (int(float(current_val)) if pd.notna(current_val) else 0) + quantity
                df.at[idx, df.columns[material_col_idx]] = new_val
                updated = True
                break
        
        if not updated:
            return {'success': False, 'error': '找不到有效的機型可以入庫'}
        
        # 寫回 Excel
        with pd.ExcelWriter(casting_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=xl.sheet_names[sheet_idx], index=False)
        
        # 清除快取
        global INVENTORY_CACHE
        INVENTORY_CACHE['data'] = None
        INVENTORY_CACHE['mtime'] = 0
        
        return {
            'success': True,
            'message': f'{part_name} 入庫成功，已增加 {quantity} 件到素材',
            'quantity': quantity
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def stock_out_product(part_name, work_order, quantity):
    """
    出庫操作 - 扣除成品數量
    
    Args:
        part_name: 零件名稱 (工作台/底座/橫樑/立柱)
        work_order: 工單號碼
        quantity: 出庫數量
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        from flask import current_app
        import pandas as pd
        import os
        
        casting_file = current_app.config['CASTING_FILE']
        
        # 零件對應的工作表索引
        sheet_mapping = {
            '底座': 1,
            '工作台': 2,
            '橫樑': 3,
            '立柱': 4
        }
        
        # 成品欄位索引 (根據 CONFIGS)
        product_col_mapping = {
            '底座': 6,      # 成品研磨
            '工作台': 7,    # 成品
            '橫樑': 6,      # 成品研磨
            '立柱': 5       # 成品研磨
        }
        
        if part_name not in sheet_mapping:
            return {'success': False, 'error': f'未知的零件名稱: {part_name}'}
        
        sheet_idx = sheet_mapping[part_name]
        product_col_idx = product_col_mapping[part_name]
        
        # 讀取 Excel 檔案
        xl = pd.ExcelFile(casting_file)
        df = pd.read_excel(xl, sheet_name=sheet_idx)
        
        # 計算當前成品總數
        current_total = 0
        for _, row in df.iterrows():
            model = row.get('機型', '')
            if pd.notna(model) and str(model).strip() and str(model).strip() != '品號':
                val = row.iloc[product_col_idx]
                if pd.notna(val):
                    try:
                        current_total += int(float(val))
                    except:
                        pass
        
        if current_total < quantity:
            return {'success': False, 'error': f'成品數量不足！當前成品: {current_total}，需要: {quantity}'}
        
        # 從成品中扣除數量 (從第一個有庫存的機型開始扣)
        remaining = quantity
        for idx, row in df.iterrows():
            if remaining <= 0:
                break
                
            model = row.get('機型', '')
            if pd.notna(model) and str(model).strip() and str(model).strip() != '品號':
                current_val = row.iloc[product_col_idx]
                if pd.notna(current_val):
                    try:
                        current_qty = int(float(current_val))
                        if current_qty > 0:
                            deduct = min(current_qty, remaining)
                            df.at[idx, df.columns[product_col_idx]] = current_qty - deduct
                            remaining -= deduct
                    except:
                        pass
        
        # 寫回 Excel
        with pd.ExcelWriter(casting_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=xl.sheet_names[sheet_idx], index=False)
        
        # 清除快取
        global INVENTORY_CACHE
        INVENTORY_CACHE['data'] = None
        INVENTORY_CACHE['mtime'] = 0
        
        return {
            'success': True,
            'message': f'{part_name} 出庫成功，工單 {work_order}，已扣除 {quantity} 件成品',
            'work_order': work_order,
            'quantity': quantity
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

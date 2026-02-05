
def stock_in_material(part_name, quantity, model=None, supplier=None):
    """
    入庫操作 - 增加素材數量
    """
    try:
        from flask import current_app, session
        import pandas as pd
        
        # 嘗試在模組內引用 log_edit，如果不行的話可能需要重新組織代碼
        # 由於 log_edit 就在同一個模組，應該可以直接使用，但因為我們是覆寫，
        # 需要確保在函數內部能訪問到。
        # 為了安全起見，如果此函數在 inventory.py 底部，它應該能看到上面的 log_edit
        
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
        
        # 動態決定素材欄位索引
        config = CONFIGS.get(part_name, [])
        material_col_idx = 2  # 預設值
        for label, idx in config:
            if label == '素材':
                material_col_idx = idx
                break
        
        # 讀取 Excel 檔案
        xl = pd.ExcelFile(casting_file)
        df = pd.read_excel(xl, sheet_name=sheet_idx)
        
        updated = False
        log_data = None
        
        # 根據品號 (model) 更新
        if model:
            search_part_no = str(model).strip()
            for idx, row in df.iterrows():
                # 第0欄是品號
                curr_part_no = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                
                # 如果品號匹配
                if curr_part_no == search_part_no:
                    current_val = row.iloc[material_col_idx]
                    old_v = int(float(current_val)) if pd.notna(current_val) else 0
                    new_val = old_v + quantity
                    df.at[idx, df.columns[material_col_idx]] = new_val
                    updated = True
                    
                    log_data = {
                        'item_id': curr_part_no,
                        'old_value': old_v,
                        'new_value': new_val
                    }
                    break
        
        # 如果沒有指定品號，或找不到品號，則使用舊邏輯 (找第一個有效機型)
        if not updated and not model:
            for idx, row in df.iterrows():
                model_val = row.get('機型', '')
                if pd.notna(model_val) and str(model_val).strip() and str(model_val).strip() != '品號':
                    current_val = row.iloc[material_col_idx]
                    old_v = int(float(current_val)) if pd.notna(current_val) else 0
                    new_val = old_v + quantity
                    df.at[idx, df.columns[material_col_idx]] = new_val
                    updated = True

                    log_data = {
                        'item_id': str(model_val).strip(), # 如果沒有品號，用機型名暫代
                        'old_value': old_v,
                        'new_value': new_val
                    }
                    break
        
        if not updated:
            if model:
                return {'success': False, 'error': f'找不到指定的品號: {model}'}
            else:
                return {'success': False, 'error': '找不到有效的機型可以入庫'}
        
        # 寫回 Excel
        with pd.ExcelWriter(casting_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=xl.sheet_names[sheet_idx], index=False)
        
        # 寫入履歷
        if log_data:
            user_id = session.get('user', 'System')
            field_name = '素材'
            if supplier:
                field_name += f' (入庫: {supplier})'
            else:
                field_name += ' (入庫)'
                
            try:
                log_edit(part_name, log_data['item_id'], field_name, 
                         log_data['old_value'], log_data['new_value'], user_id)
            except Exception as e:
                print(f"Failed to log edit: {e}")

        msg = f'{part_name} 入庫成功，已增加 {quantity} 件到素材'
        if model:
            msg += f' (品號: {model})'
        if supplier:
            msg += f'，供應商: {supplier}'
            
        return {
            'success': True,
            'message': msg,
            'quantity': quantity
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def stock_out_product(part_name, work_order, quantity, model=None):
    """
    出庫操作 - 扣除成品數量
    """
    try:
        from flask import current_app, session
        import pandas as pd
        
        casting_file = current_app.config['CASTING_FILE']
        
        sheet_mapping = {
            '底座': 1,
            '工作台': 2,
            '橫樑': 3,
            '立柱': 4
        }
        
        if part_name not in sheet_mapping:
            return {'success': False, 'error': f'未知的零件名稱: {part_name}'}
        
        sheet_idx = sheet_mapping[part_name]
        
        # 動態決定成品欄位索引
        config = CONFIGS.get(part_name, [])
        product_col_idx = None
        product_label = '成品'
        for label, idx in config:
            if label in ['成品', '成品研磨']:
                product_col_idx = idx
                product_label = label
                break
        
        if product_col_idx is None:
            return {'success': False, 'error': f'找不到 {part_name} 的成品欄位'}

        xl = pd.ExcelFile(casting_file)
        df = pd.read_excel(xl, sheet_name=sheet_idx)
        
        updated = False
        log_data = None
        
        # 邏輯 A: 指定品號出庫
        if model:
            search_part_no = str(model).strip()
            target_idx = -1
            
            # 尋找目標行
            for idx, row in df.iterrows():
                curr_part_no = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                if curr_part_no == search_part_no:
                    target_idx = idx
                    val = row.iloc[product_col_idx]
                    current_stock = int(float(val)) if pd.notna(val) else 0
                    break
            
            if target_idx == -1:
                return {'success': False, 'error': f'找不到指定的品號: {model}'}
            
            if current_stock < quantity:
                return {'success': False, 'error': f'庫存不足！品號 {model} 當前成品: {current_stock}，需要: {quantity}'}
            
            # 執行扣除
            new_val = current_stock - quantity
            df.at[target_idx, df.columns[product_col_idx]] = new_val
            updated = True
            
            log_data = {
                'item_id': search_part_no,
                'old_value': current_stock,
                'new_value': new_val
            }
            
        # 邏輯 B: 未指定品號
        else:
            # 省略舊邏輯的 log，因為現在都強制選機型了
            # 如果真的跑進來這裡，我們就只記錄操作成功，數字可能不太精確因為是扣多行
            
            # 計算總庫存
            current_total = 0
            for _, row in df.iterrows():
                m_val = row.get('機型', '')
                if pd.notna(m_val) and str(m_val).strip() and str(m_val).strip() != '品號':
                    val = row.iloc[product_col_idx]
                    if pd.notna(val):
                        try:
                            current_total += int(float(val))
                        except:
                            pass
            
            if current_total < quantity:
                return {'success': False, 'error': f'該零件總成品數量不足！當前: {current_total}，需要: {quantity}'}
            
            # 從成品中扣除數量
            remaining = quantity
            for idx, row in df.iterrows():
                if remaining <= 0:
                    break
                    
                m_val = row.get('機型', '')
                if pd.notna(m_val) and str(m_val).strip() and str(m_val).strip() != '品號':
                    current_val = row.iloc[product_col_idx]
                    if pd.notna(current_val):
                        try:
                            current_qty = int(float(current_val))
                            if current_qty > 0:
                                deduct = min(current_qty, remaining)
                                df.at[idx, df.columns[product_col_idx]] = current_qty - deduct
                                remaining -= deduct
                                updated = True
                        except:
                            pass
        
        if not updated:
             return {'success': False, 'error': '出庫操作未能完成，請檢查庫存狀態'}

        # 寫回 Excel
        with pd.ExcelWriter(casting_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=xl.sheet_names[sheet_idx], index=False)
            
        # 寫入履歷
        # 如果是邏輯A (有log_data)，我們記錄精確值
        if log_data:
            user_id = session.get('user', 'System')
            field_name = f'{product_label} (出庫: 工單 {work_order})'
            try:
                log_edit(part_name, log_data['item_id'], field_name, 
                         log_data['old_value'], log_data['new_value'], user_id)
            except Exception as e:
                print(f"Failed to log edit: {e}")
        
        # 如果是邏輯B，我們目前沒辦法精確記錄單一 item_id 的變化，除非記錄多筆
        # 暫時不處理邏輯B的 Log，因為前端已經強制要選機型了。
        
        return {
            'success': True,
            'message': f'{part_name} 出庫成功，工單 {work_order}，已扣除 {quantity} 件成品',
            'work_order': work_order,
            'quantity': quantity
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

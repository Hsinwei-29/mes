import pandas as pd
from flask import current_app

def load_casting_inventory():
    """載入鑄件庫存資料"""
    try:
        casting_file = current_app.config['CASTING_FILE']
        xl = pd.ExcelFile(casting_file)
        df = pd.read_excel(xl, sheet_name='總數')
        
        # 取得庫存總計
        inventory = {
            '底座': df['底座'].sum() if '底座' in df.columns else 0,
            '工作台': df['工作台'].sum() if '工作台' in df.columns else 0,
            '橫樑': df['橫樑'].sum() if '橫樑' in df.columns else 0,
            '立柱': df['立柱'].sum() if '立柱' in df.columns else 0,
        }
        
        # 轉換 NaN 為 0
        for key in inventory:
            if pd.isna(inventory[key]):
                inventory[key] = 0
            else:
                inventory[key] = int(inventory[key])
        
        # 按機型整理詳細資料
        details = []
        for _, row in df.iterrows():
            model = row['機型'] if '機型' in df.columns else row.iloc[0]
            detail = {'機型': str(model)}
            for col in ['底座', '工作台', '橫樑', '立柱']:
                if col in df.columns:
                    val = row[col]
                    detail[col] = 0 if pd.isna(val) else int(val)
                else:
                    detail[col] = 0
            # 只加入有庫存的機型
            if any(detail[col] > 0 for col in ['底座', '工作台', '橫樑', '立柱']):
                details.append(detail)
        
        return {'summary': inventory, 'details': details}
    except Exception as e:
        print(f"Error loading casting inventory: {e}")
        return {'summary': {}, 'details': [], 'error': str(e)}

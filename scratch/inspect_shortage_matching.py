import sys
import os
import pandas as pd

# Ensure the root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
app = create_app('production')

with app.app_context():
    from app.models.shortage import get_casting_inventory
    from app.models.order import get_picking_data, PICKING_CACHE
    
    # Load inputs
    casting_inv = get_casting_inventory()
    get_picking_data()
    raw_df = PICKING_CACHE.get('raw_df')
    
    print(f"Total casting_inventory keys: {len(casting_inv)}")
    print(f"Casting sample keys: {list(casting_inv.keys())[:10]}")
    
    # Load workorder keys from Excel
    workorder_file = app.config['WORKORDER_FILE']
    wo_df = pd.read_excel(workorder_file, sheet_name=0, engine='calamine')
    wo_keys = []
    for _, row in wo_df.iterrows():
        try:
            wo_number = str(int(float(row['工單號碼']))) if pd.notna(row['工單號碼']) else None
        except:
            wo_number = str(row['工單號碼']).strip() if pd.notna(row['工單號碼']) else None
        if wo_number:
            wo_keys.append(wo_number)
    print(f"Total workorder keys from Excel: {len(wo_keys)}")
    print(f"Workorder sample keys: {wo_keys[:10]}")
    
    print(f"\nTotal raw_df rows: {len(raw_df)}")
    
    # Check if there are any matches on Part Number
    print("\nPart Number Matching Check:")
    matched_parts = 0
    sample_part_matches = []
    for _, row in raw_df.iterrows():
        part_full = str(row['物料']).strip() if pd.notna(row['物料']) else ""
        part_base = part_full[:10]
        if part_base in casting_inv:
            matched_parts += 1
            if len(sample_part_matches) < 5:
                sample_part_matches.append((part_full, part_base))
    print(f"Total rows in raw_df matching casting inventory part: {matched_parts}")
    print(f"Sample part matches: {sample_part_matches}")
    
    # Check if there are any matches on Order (工單) Number
    print("\nOrder Number Matching Check:")
    matched_orders = 0
    sample_order_matches = []
    for _, row in raw_df.iterrows():
        try:
            order_num = str(int(float(row['訂單']))) if pd.notna(row['訂單']) else ""
        except:
            order_num = str(row['訂單']).strip() if pd.notna(row['訂單']) else ""
        if order_num in wo_keys:
            matched_orders += 1
            if len(sample_order_matches) < 5:
                sample_order_matches.append(order_num)
    print(f"Total rows in raw_df matching workorders: {matched_orders}")
    print(f"Sample order matches: {sample_order_matches}")
    
    # Check joint matches (Part AND Order)
    joint_matches = 0
    for _, row in raw_df.iterrows():
        part_full = str(row['物料']).strip() if pd.notna(row['物料']) else ""
        part_base = part_full[:10]
        try:
            order_num = str(int(float(row['訂單']))) if pd.notna(row['訂單']) else ""
        except:
            order_num = str(row['訂單']).strip() if pd.notna(row['訂單']) else ""
            
        if part_base in casting_inv and order_num in wo_keys:
            joint_matches += 1
    print(f"\nTotal rows matching BOTH part and order: {joint_matches}")

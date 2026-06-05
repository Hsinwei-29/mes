import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DELIVERY_FILE = os.path.join(DATA_DIR, 'delivery.json')
SHIPPING_FILE = os.path.join(DATA_DIR, 'shipping.json')
DELETED_RECORDS_FILE = os.path.join(DATA_DIR, 'deleted_records.json')

def log_deleted_record(record_type, record, user):
    deleted_records = load_json(DELETED_RECORDS_FILE)
    deleted_records.append({
        'deleted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'deleted_by': user,
        'record_type': record_type,
        'record_data': record
    })
    save_json(DELETED_RECORDS_FILE, deleted_records)

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Error reading {filepath}: {e}")
        import shutil
        import time
        try:
            backup_file = f"{filepath}.corrupted.{int(time.time())}"
            shutil.copy2(filepath, backup_file)
            print(f"Backed up corrupted file to {backup_file}")
        except:
            pass
        return []

def save_json(filepath, data):
    ensure_data_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- Delivery Records ---
def get_delivery_records():
    return load_json(DELIVERY_FILE)

def add_delivery_record(record):
    records = get_delivery_records()
    if 'id' not in record:
        record['id'] = int(datetime.now().timestamp() * 1000)
    records.append(record)
    save_json(DELIVERY_FILE, records)
    return record

def update_delivery_record(record_id, field, value):
    records = get_delivery_records()
    for r in records:
        if r['id'] == record_id:
            r[field] = value
            save_json(DELIVERY_FILE, records)
            return True
    return False

def delete_delivery_record(record_id, user="Unknown"):
    records = get_delivery_records()
    record_to_delete = next((r for r in records if r['id'] == record_id), None)
    new_records = [r for r in records if r['id'] != record_id]
    if len(new_records) != len(records):
        save_json(DELIVERY_FILE, new_records)
        if record_to_delete:
            log_deleted_record('delivery', record_to_delete, user)
        return True
    return False

# --- Shipping Records ---
def get_shipping_records():
    return load_json(SHIPPING_FILE)

def add_shipping_request(record):
    records = get_shipping_records()
    if 'id' not in record:
        record['id'] = int(datetime.now().timestamp() * 1000)
    if 'status' not in record:
        record['status'] = '簽核'
    records.append(record)
    save_json(SHIPPING_FILE, records)
    return record

def delete_shipping_record(record_id, user="Unknown"):
    records = get_shipping_records()
    record_to_delete = next((r for r in records if r['id'] == record_id), None)
    new_records = [r for r in records if r['id'] != record_id]
    if len(new_records) != len(records):
        save_json(SHIPPING_FILE, new_records)
        if record_to_delete:
            log_deleted_record('shipping', record_to_delete, user)
        return True
    return False

def update_shipping_signature(record_id, role, name, img_data):
    records = get_shipping_records()
    for r in records:
        if r['id'] == record_id:
            if 'signatures' not in r:
                r['signatures'] = {}
            r['signatures'][role] = {
                'name': name,
                'img': img_data,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 檢查是否已完全核准 (如果是最後一關)
            if role == '下流程簽收':
                r['status'] = '已核准'
                
            save_json(SHIPPING_FILE, records)
            return True
    return False

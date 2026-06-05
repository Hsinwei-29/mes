import json

file_path = 'logs/lifting_history.json'
with open(file_path, 'r', encoding='utf-8') as f:
    history = json.load(f)

# Add the record that was in the truncated file
record = {
    "timestamp": "2026-06-01 09:00:45",
    "category": "吊具",
    "item_id": "F006106",
    "action": "領用",
    "user": "喬賽多"
}

# Check if it already exists
if not any(h.get('timestamp') == record['timestamp'] and h.get('item_id') == record['item_id'] for h in history):
    history.insert(0, record)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print("Record added.")
else:
    print("Record already exists.")

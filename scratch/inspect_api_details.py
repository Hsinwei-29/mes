import urllib.request
import json

api_url = "http://192.168.6.119:5002/api/finished_materials"

try:
    with urllib.request.urlopen(api_url, timeout=10) as response:
        content = response.read().decode('utf-8')
        json_data = json.loads(content)
        
        non_empty_count = 0
        total_details_count = 0
        
        for idx, item in enumerate(json_data):
            details = item.get('demand_details', [])
            if details and len(details) > 0:
                non_empty_count += 1
                total_details_count += len(details)
                if non_empty_count <= 5:
                    print(f"Sample non-empty item at index {idx}:")
                    print(f"  物料: {item.get('物料')}")
                    print(f"  物料說明: {item.get('物料說明')}")
                    print(f"  demand_details length: {len(details)}")
                    print(f"  First detail: {details[0]}")
                    
        print(f"\nSummary:")
        print(f"  Total items: {len(json_data)}")
        print(f"  Items with non-empty demand_details: {non_empty_count}")
        print(f"  Total demand details found: {total_details_count}")
        
except Exception as e:
    print(f"Error: {e}")

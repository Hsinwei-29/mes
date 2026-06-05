import pickle
import os

cache_dir = '/home/hsinwei/app/mes/app/cache'
cache_file = os.path.join(cache_dir, 'shortage_cache.pkl')

report_file = '/home/hsinwei/app/mes/scratch/shortage_report.txt'

if not os.path.exists(cache_file):
    with open(report_file, 'w') as f:
        f.write("Cache file does not exist!")
else:
    with open(cache_file, 'rb') as f:
        cached = pickle.load(f)
    
    shortages = [x for x in cached['data'] if x['缺料數量'] > 0]
    
    with open(report_file, 'w') as f:
        f.write(f"Total shortage rows in cache: {len(shortages)}\n\n")
        for x in shortages:
            f.write(f"工單: {x.get('工單編碼') or x.get('工單號碼')}, 客戶: {x.get('客戶名稱')}, 品號: {x.get('品號')}, 結束: {x.get('生產結束')}, 需求: {x.get('需求數量')}, 已領: {x.get('已領料')}, 缺料: {x.get('缺料數量')}, 備註: {x.get('特規備註')}\n")
    print("Report written successfully!")

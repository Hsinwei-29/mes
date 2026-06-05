import pickle
import os

cache_dir = '/home/hsinwei/app/mes/app/cache'
cache_file = os.path.join(cache_dir, 'orders_cache.pkl')
report_file = '/home/hsinwei/app/mes/scratch/orders_cache_report.txt'

if not os.path.exists(cache_file):
    with open(report_file, 'w') as f:
        f.write("Cache file does not exist!")
else:
    with open(cache_file, 'rb') as f:
        cached = pickle.load(f)
    
    orders = cached['data']['orders']
    stats = cached['data']['stats']
    non_zero = [o for o in orders if o['需求_底座'] > 0 or o['需求_工作台'] > 0 or o['需求_橫樑'] > 0 or o['需求_立柱'] > 0]
    
    with open(report_file, 'w') as f:
        f.write(f"Stats: {stats}\n")
        f.write(f"Total orders: {len(orders)}\n")
        f.write(f"Total orders with populated needs: {len(non_zero)}\n\n")
        for o in non_zero[:15]:
            f.write(f"工單: {o['工單']}, 客戶: {o['客戶']}, 底座: {o['需求_底座']}, 工作台: {o['需求_工作台']}, 橫樑: {o['需求_橫樑']}, 立柱: {o['需求_立柱']}, 狀態: {o.get('狀態')}\n")
print("Done!")

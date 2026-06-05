import sys
sys.path.insert(0, '/home/hsinwei/app/mes')

import os
import pickle
from app import create_app
from app.models.order import PICKING_CACHE, get_picking_data
from app.models.shortage import calculate_shortage

app = create_app('production')

with app.app_context():
    print("=== FORCING CACHE INVALIDATION & REBUILD ===")
    
    # 1. Clear in-memory cache variable state (current thread context)
    PICKING_CACHE['mtime'] = 0
    PICKING_CACHE['data'] = None
    PICKING_CACHE['raw_df'] = None
    
    # 2. Locate and delete all cache files on disk to force rebuilding from scratch
    cache_dir = os.path.join(os.getcwd(), 'app', 'cache')
    picking_cache_file = os.path.join(cache_dir, 'picking_cache.pkl')
    shortage_cache_file = os.path.join(cache_dir, 'shortage_cache.pkl')
    orders_cache_file = os.path.join(cache_dir, 'orders_cache.pkl')
    
    for f_path in [picking_cache_file, shortage_cache_file, orders_cache_file]:
        if os.path.exists(f_path):
            try:
                os.remove(f_path)
                print(f"✅ Removed disk cache: {os.path.basename(f_path)}")
            except Exception as e:
                print(f"❌ Failed to delete {os.path.basename(f_path)}: {e}")
                
    # 3. Pull fresh picking data from the API
    print("\n🌐 Fetching fresh Finished Product Picking data from API...")
    picking_data = get_picking_data()
    print(f"✅ API fetch successful! Loaded {len(picking_data)} orders from API.")
    
    # 4. Trigger shortage recalculation to regenerate shortage cache
    print("\n🔄 Recalculating shortage with new data...")
    shortage_data = calculate_shortage()
    shortage_items = [x for x in shortage_data if x['缺料數量'] > 0]
    print(f"✅ Shortage calculated! Total items: {len(shortage_data)}, Shortage items: {len(shortage_items)}")
    
    print("\n=== CACHE REBUILD COMPLETE ===")

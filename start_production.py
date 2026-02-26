"""
MES 系統生產環境啟動腳本
使用 Waitress WSGI 伺服器（生產級）
"""
from waitress import serve
from app import create_app
import os

# 創建應用
app = create_app('production')

def warm_up_cache(app):
    """Background cache warm-up on server start"""
    import threading
    def _warm():
        try:
            with app.app_context():
                print("[Cache Warm-up] Start...")
                from app.models.inventory import load_casting_inventory
                from app.models.order import load_orders
                from app.models.shortage import calculate_shortage
                load_casting_inventory()
                print("[Cache Warm-up] OK: inventory")
                load_orders()
                print("[Cache Warm-up] OK: orders")
                calculate_shortage()
                print("[Cache Warm-up] OK: shortage - All done! First page load will be fast.")
        except Exception as e:
            print(f"[Cache Warm-up] WARN: {e}")
    threading.Thread(target=_warm, daemon=True).start()


if __name__ == '__main__':
    # 設置日誌
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/mes_system.log'),
            logging.StreamHandler()
        ]
    )

    # 確保日誌目錄存在
    os.makedirs('logs', exist_ok=True)

    print("="*60)
    print("MES Starting...")
    print("="*60)
    print(f"URL: http://0.0.0.0:5010")
    print(f"Press Ctrl+C to stop")
    print("="*60)

    # Background cache warm-up
    warm_up_cache(app)

    # 使用 Waitress 啟動（生產級）
    serve(app, host='0.0.0.0', port=5010, threads=4)

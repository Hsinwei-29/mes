import os
import socket
from app import create_app, socketio

# 取得配置名稱，預設為 production
config_name = os.getenv('FLASK_CONFIG', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    # 取得本機 IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"

    print("=" * 60)
    print("[MVC Mode] 加工鑄件即時看板伺服器 (WebSocket Enabled)")
    print("=" * 60)
    print(f"[OK] 伺服器已啟動！")
    print(f"Local URL: http://localhost:5010")
    print(f"LAN URL: http://{local_ip}:5010")
    print("=" * 60)
    print("按 Ctrl+C 停止伺服器")
    
    # 使用 SocketIO 啟動 (支援 WebSocket)
    socketio.run(app, host='0.0.0.0', port=5010, debug=False, allow_unsafe_werkzeug=True)

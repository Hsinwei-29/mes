from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_login import LoginManager
from config import config
import os

# 全域 SocketIO 實例
socketio = SocketIO()
login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__, 
                template_folder='views/templates', 
                static_folder='views/static')
    
    # 載入配置
    app.config.from_object(config[config_name])
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['CASTING_FILE'] = '鑄件盤點資料.xlsx'
    
    # Session 配置 - 使用 Cookie-based sessions
    app.config['SESSION_COOKIE_SECURE'] = False  # 開發環境設為 False，生產環境應設為 True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
    
    # 啟用 CORS with credentials support
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    
    # 初始化 SocketIO
    socketio.init_app(app, cors_allowed_origins="*")
    
    # 初始化 Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '請先登入'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.get_by_id(user_id)
    
    # 註冊 Blueprints
    from .controllers.main import main_bp
    from .controllers.api import api_bp
    from .controllers.auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp)

    # ── 背景預熱快取 ────────────────────────────────────────────────
    def _warmup_cache():
        """伺服器啟動後在背景預先載入所有耗時資料，讓第一次使用者請求秒回。"""
        import time
        with app.app_context():
            try:
                t0 = time.time()
                print("[WARMUP] 開始預熱快取...")
                from app.models.inventory import load_casting_inventory
                load_casting_inventory()
                print(f"[WARMUP] inventory OK ({(time.time()-t0)*1000:.0f} ms)")

                from app.models.order import load_orders
                load_orders()
                print(f"[WARMUP] orders OK ({(time.time()-t0)*1000:.0f} ms)")

                from app.models.shortage import calculate_shortage
                calculate_shortage()
                print(f"[WARMUP] shortage OK ({(time.time()-t0)*1000:.0f} ms)")

                from app.models.lifting import load_lifting_inventory
                load_lifting_inventory()
                print(f"[WARMUP] lifting OK ({(time.time()-t0)*1000:.0f} ms)")

                print(f"[WARMUP] 快取預熱完成，總耗時 {(time.time()-t0)*1000:.0f} ms")
            except Exception as e:
                print(f"[WARMUP] 預熱失敗: {e}")

    import threading
    _t = threading.Thread(target=_warmup_cache, daemon=True, name="cache-warmup")
    _t.start()

    # ── 背景定時更新快取 (每天 09:00 與 17:00) ──────────────────────
    def _schedule_daily_updates():
        import time
        from datetime import datetime
        last_run_tag = None
        while True:
            try:
                now = datetime.now()
                # 判斷是否在 09:00~09:05 或 17:00~17:05 之間觸發
                # (容錯 5 分鐘，避免剛好錯過 0 分)
                if (now.hour == 9 or now.hour == 17) and now.minute < 5:
                    run_tag = now.strftime('%Y%m%d_%H')
                    if last_run_tag != run_tag:
                        with app.app_context():
                            print(f"[SCHEDULE] 執行每日定時更新缺料與工單系統 ({run_tag})...")
                            from app.models.order import load_orders
                            from app.models.shortage import calculate_shortage
                            load_orders()
                            calculate_shortage()
                            print(f"[SCHEDULE] 定時更新完成。")
                        last_run_tag = run_tag
            except Exception as e:
                print(f"[SCHEDULE] 排程錯誤: {e}")
            time.sleep(60)

    _t_sched = threading.Thread(target=_schedule_daily_updates, daemon=True, name="daily-schedule")
    _t_sched.start()
    # ────────────────────────────────────────────────────────────────

    return app

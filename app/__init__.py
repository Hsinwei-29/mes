from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from config import config

# 全域 SocketIO 實例
socketio = SocketIO()

def create_app(config_name='default'):
    app = Flask(__name__, 
                template_folder='views/templates', 
                static_folder='views/static')
    
    # 載入配置
    app.config.from_object(config[config_name])
    app.config['SECRET_KEY'] = app.config.get('SECRET_KEY', 'mes-dashboard-secret-key-2026')
    
    # 啟用 CORS
    CORS(app)
    
    # 初始化 SocketIO
    socketio.init_app(app, cors_allowed_origins="*")
    
    # 註冊 Blueprints
    from .controllers.main import main_bp
    from .controllers.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

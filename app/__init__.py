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
    
    # 啟用 CORS
    CORS(app)
    
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
    
    return app

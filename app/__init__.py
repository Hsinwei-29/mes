from flask import Flask
from flask_cors import CORS
from config import config

def create_app(config_name='default'):
    app = Flask(__name__, 
                template_folder='views/templates', 
                static_folder='views/static')
    
    # 載入配置
    app.config.from_object(config[config_name])
    
    # 啟用 CORS
    CORS(app)
    
    # 註冊 Blueprints
    from .controllers.main import main_bp
    from .controllers.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

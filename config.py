import os

class Config:
    # 基礎目錄
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = BASE_DIR
    
    # 資料檔案路徑
    CASTING_FILE = os.path.join(DATA_DIR, '鑄件盤點資料.xlsx')
    WORKORDER_FILE = os.path.join(DATA_DIR, '工單總表2026.xls')
    PICKING_FILE = os.path.join(DATA_DIR, '成品撥料.XLSX')
    
    # 應用程式設定
    DEBUG = False
    PORT = 5000
    HOST = '0.0.0.0'
    THREADS = 6

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}

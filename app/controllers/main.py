from flask import Blueprint, render_template
from flask_login import current_user
from datetime import datetime

main_bp = Blueprint('main', __name__)

# 鑄件圖示對應
PART_ICONS = {
    '底座': '🔲',
    '工作台': '🔳',
    '橫樑': '📏',
    '立柱': '🏛️'
}

@main_bp.route('/')
def index():
    """主頁面 - 庫存看板"""
    return render_template('main/index.html')

@main_bp.route('/orders')
def orders_page():
    """工單需求頁面"""
    return render_template('main/orders.html')

@main_bp.route('/casting/<part_type>')
def casting_page(part_type):
    """全頁式鑄件製程編輯頁面"""
    from ..models.inventory import get_part_details
    
    data = get_part_details(part_type)
    headers = data.get('headers', [])
    rows = data.get('rows', [])
    
    # 使用 Flask-Login 的 current_user 檢查登入狀態
    is_logged_in = current_user.is_authenticated
    is_admin = current_user.is_admin() if is_logged_in else False
    username = current_user.username if is_logged_in else None
    
    # 生成時間戳記
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"[DEBUG] is_logged_in={is_logged_in}, is_admin={is_admin}, user={username}")  # Debug
    
    return render_template('main/casting.html',
                          part_name=part_type,
                          part_icon=PART_ICONS.get(part_type, '📦'),
                          headers=headers,
                          rows=rows,
                          is_logged_in=is_logged_in,
                          is_admin=is_admin,
                          current_user=username,
                          timestamp=timestamp)

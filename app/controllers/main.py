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

@main_bp.route('/shortage')
def shortage_page():
    """缺料分析頁面"""
    return render_template('main/shortage.html')

@main_bp.route('/part/<part_type>')
def part_detail_page(part_type):
    """鑄件半品成品詳細頁面"""
    from ..models.inventory import get_part_details
    
    data = get_part_details(part_type)
    
    # 計算半品和成品總數
    semi_finished_fields = {
        '底座': ['素材', 'M4', 'M3'],
        '工作台': ['素材', 'W1', 'W2', 'W3', 'W4'],
        '橫樑': ['素材', 'M6', 'M5'],
        '立柱': ['素材', '半品', '成品銑工']
    }
    
    finished_fields = {
        '底座': ['成品研磨'],
        '工作台': ['成品'],
        '橫樑': ['成品研磨'],
        '立柱': ['成品研磨']
    }
    
    total_semi = 0
    total_finished = 0
    
    for row in data.get('rows', []):
        # 計算半品
        for field in semi_finished_fields.get(part_type, []):
            total_semi += row.get(field, 0)
        
        # 計算成品
        for field in finished_fields.get(part_type, []):
            total_finished += row.get(field, 0)
    
    # 計算需求量（從缺料分析，只計算實際缺料的數量）
    from ..models.shortage import calculate_shortage
    shortage_list = calculate_shortage()
    
    total_demand = 0
    for item in shortage_list:
        if item.get('零件類型', '') == part_type and item.get('缺料數量', 0) > 0:
            total_demand += item.get('缺料數量', 0)
    
    # 使用 Flask-Login 的 current_user 檢查登入狀態
    is_logged_in = current_user.is_authenticated
    username = current_user.username if is_logged_in else None
    
    # 生成時間戳記
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('main/part_detail.html',
                          part_name=part_type,
                          part_icon=PART_ICONS.get(part_type, '📦'),
                          data=data,
                          total_semi=total_semi,
                          total_finished=total_finished,
                          total_demand=total_demand,
                          current_user=username,
                          timestamp=timestamp)

@main_bp.route('/model-search')
def model_search_page():
    """機型搜尋頁面"""
    return render_template('main/model_search.html')

@main_bp.route('/lifting')
def lifting_page():
    """吊具管理頁面"""
    is_logged_in = current_user.is_authenticated
    return render_template('main/lifting.html', is_logged_in=is_logged_in)

@main_bp.route('/test-api')
def test_api_page():
    """API 測試頁面"""
    return render_template('test_api.html')


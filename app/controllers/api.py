from flask import Blueprint, jsonify, request, session
from flask_login import login_required, current_user
from datetime import datetime
from ..models.inventory import load_casting_inventory, get_part_details, update_cell, get_edit_history, get_zero_inventory_models
from ..models.order import load_orders
from .. import socketio

api_bp = Blueprint('api', __name__)

def calculate_supply_demand():
    """計算供需狀況"""
    from ..models.shortage import calculate_shortage
    
    inventory = load_casting_inventory()
    
    supply = inventory.get('summary', {})
    semi_finished = inventory.get('semi_finished', {})
    finished = inventory.get('finished', {})
    
    # 從缺料分析取得真實需求（只計算實際缺料的數量）
    shortage_list = calculate_shortage()
    
    # 計算各鑄件的缺料數量
    demand = {'工作台': 0, '底座': 0, '橫樑': 0, '立柱': 0}
    for item in shortage_list:
        part_type = item.get('零件類型', '')
        shortage_qty = item.get('缺料數量', 0)
        if part_type in demand and shortage_qty > 0:
            demand[part_type] += shortage_qty
    
    analysis = []
    for part in ['工作台', '底座', '橫樑', '立柱']:
        stock = supply.get(part, 0)
        semi = semi_finished.get(part, 0)
        fin = finished.get(part, 0)
        need = demand.get(part, 0)
        diff = stock - need
        status = '充足' if diff >= 0 else '不足'
        analysis.append({
            '鑄件': part, 
            '庫存': stock, 
            '半品': semi,
            '成品': fin,
            '需求': need, 
            '差異': diff, 
            '狀態': status
        })
    return analysis

@api_bp.route('/inventory')
def api_inventory():
    data = load_casting_inventory()
    data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(data)

@api_bp.route('/orders')
def api_orders():
    data = load_orders()
    data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(data)

@api_bp.route('/summary')
@api_bp.route('/summary_v2')
def api_summary():
    inventory = load_casting_inventory()
    orders = load_orders()
    supply_demand = calculate_supply_demand()
    
    result = {
        'inventory': inventory.get('summary', {}),
        'inventory_details': inventory.get('details', []),
        'orders_stats': orders.get('stats', {}),
        'supply_demand': supply_demand,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 加入 no-cache headers
    response = jsonify(result)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@api_bp.route('/inventory/zero-stock')
def api_zero_stock():
    """獲取總數為0的鑄件機型"""
    zero_models = get_zero_inventory_models()
    return jsonify({
        'zero_models': zero_models,
        'count': len(zero_models),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@api_bp.route('/part/<part_type>')
def api_part_summary(part_type):
    """獲取特定鑄件的半品成品明細"""
    try:
        details = get_part_details(part_type)
        return jsonify(details)
    except Exception as e:
        return jsonify({'error': str(e), 'items': []}), 500


@api_bp.route('/search-model/<model_name>')
def api_search_model(model_name):
    """搜尋特定機型在所有鑄件中的半品成品數量"""
    try:
        inventory = load_casting_inventory()
        semi_finished = inventory.get('semi_finished', {})
        finished = inventory.get('finished', {})
        all_models = inventory.get('all_models', {})
        
        # 查找機型
        if model_name not in all_models:
            return jsonify({'found': False, 'model': model_name, 'message': '找不到此機型'})
        
        model_data = all_models[model_name]
        
        # 取得各鑄件的詳細數據
        parts_detail = {}
        for part_name in ['工作台', '底座', '橫樑', '立柱']:
            part_details = get_part_details(part_name)
            rows = part_details.get('rows', [])
            
            # 找到該機型的資料
            model_row = next((r for r in rows if r.get('機型') == model_name), None)
            
            if model_row:
                # 根據不同零件計算半品和成品
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
                
                semi_count = sum(model_row.get(f, 0) for f in semi_finished_fields.get(part_name, []))
                finished_count = sum(model_row.get(f, 0) for f in finished_fields.get(part_name, []))
                
                parts_detail[part_name] = {
                    '半品': semi_count,
                    '成品': finished_count,
                    '總數': model_row.get('總數', 0),
                    '詳細': model_row
                }
            else:
                parts_detail[part_name] = {
                    '半品': 0,
                    '成品': 0,
                    '總數': 0
                }
        
        return jsonify({
            'found': True,
            'model': model_name,
            'parts': parts_detail,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        print(f"Error searching model: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'found': False, 'error': str(e)}), 500


@api_bp.route('/inventory/details/<part_type>')
def api_part_details(part_type):
    data = get_part_details(part_type)
    return jsonify(data)

@api_bp.route('/inventory/update/<part_type>', methods=['POST'])
def api_update_inventory(part_type):
    """更新鑄件製程數據"""
    try:
        from flask_login import current_user
        
        # 檢查用戶是否登入 (支援兩種方式)
        is_logged_in = False
        username = None
        user_role = None
        
        # 方式1: 檢查 Flask-Login
        if current_user.is_authenticated:
            is_logged_in = True
            username = current_user.username
            user_role = current_user.role
            # 同步到 session
            session['user_id'] = current_user.id
            session['username'] = current_user.username
            session['role'] = current_user.role
        # 方式2: 檢查 session
        elif 'user_id' in session:
            is_logged_in = True
            username = session.get('username', '系統使用者')
            user_role = session.get('role')
        
        if not is_logged_in:
            return jsonify({'success': False, 'error': '請先登入'}), 401
        
        if user_role != 'admin':
            return jsonify({'success': False, 'error': '僅管理員可編輯數據'}), 403
        
        data = request.get_json()
        item_id = data.get('item_id')
        model_name = data.get('model_name')
        updates = data.get('updates', {})
        
        # 使用已驗證的使用者名稱
        
        results = []
        for field, new_value in updates.items():
            result = update_cell(part_type, item_id, field, new_value, username, model_name=model_name)
            if result.get('success'):
                # 使用更新後的 item_id (如果有的話)
                actual_item_id = result.get('item_id', item_id)
                
                # 透過 SocketIO 廣播更新
                socketio.emit('data_updated', {
                    'part': part_type,
                    'item_id': actual_item_id,
                    'field': field,
                    'old_value': result.get('old_value'),
                    'new_value': new_value,
                    'total': result.get('total'),
                    'user': username,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                # 在結果中包含更新後的品號
                result['item_id'] = actual_item_id
                results.append(result)
            else:
                return jsonify({'success': False, 'error': result.get('error')})
        
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/inventory/history/<part_type>')
def api_edit_history(part_type):
    """取得修改歷程"""
    history = get_edit_history(part_type)
    return jsonify({'history': history})

@api_bp.route('/inventory/history/<part_type>/<item_id>')
def api_item_history(part_type, item_id):
    """取得特定品號的修改歷程"""
    from ..models.inventory import get_item_history
    history = get_item_history(part_type, item_id)
    return jsonify({'history': history, 'item_id': item_id})

@api_bp.route('/inventory/history/stats/<part_type>')
def api_history_stats(part_type):
    """取得歷程統計資訊"""
    from ..models.inventory import get_history_stats
    stats = get_history_stats(part_type)
    return jsonify(stats)

@api_bp.route('/shortage')
def api_shortage():
    """缺料分析 API"""
    from ..models.shortage import calculate_shortage
    
    try:
        shortage_list = calculate_shortage()
        
        # 統計資訊
        total_records = len(shortage_list)
        shortage_count = len([x for x in shortage_list if x['缺料數量'] > 0])
        
        # 按零件類型統計
        part_stats = {}
        for part_type in ['工作台', '底座', '橫樑', '立柱']:
            type_records = [x for x in shortage_list if x['零件類型'] == part_type]
            type_shortage = [x for x in type_records if x['缺料數量'] > 0]
            part_stats[part_type] = {
                'total': len(type_records),
                'shortage': len(type_shortage)
            }
            
        # 取得庫存總覽
        from ..models.inventory import load_casting_inventory
        inventory_data = load_casting_inventory()
        inventory_summary = inventory_data.get('summary', {})
        
        return jsonify({
            'success': True,
            'data': shortage_list,
            'stats': {
                'total_records': total_records,
                'shortage_count': shortage_count,
                'sufficient_count': total_records - shortage_count,
                'part_stats': part_stats,
                'inventory_summary': inventory_summary
            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/stock/in', methods=['POST'])
@login_required
def stock_in():
    """入庫 API - 增加素材數量"""
    # 檢查權限：只有管理員可以操作
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '權限不足：只有管理員可以執行入庫操作'}), 403

    try:
        data = request.get_json()
        part_name = data.get('part_name')
        quantity = data.get('quantity')
        model = data.get('model')
        supplier = data.get('supplier')
        work_order_code = data.get('work_order_code')
        
        if not part_name or not quantity:
            return jsonify({'success': False, 'error': '缺少必要參數'}), 400
        
        # 調用 inventory.py 中的入庫函數
        from ..models.inventory import stock_in_material
        result = stock_in_material(
            part_name=part_name, 
            quantity=quantity, 
            model=model, 
            supplier=supplier, 
            user=current_user.username,
            work_order_code=work_order_code
        )
        
        if result['success']:
            # 通知所有客戶端更新數據
            socketio.emit('data_updated', {'type': 'stock_in', 'part': part_name})
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/stock/out', methods=['POST'])
@login_required
def stock_out():
    """出庫 API - 扣除成品數量"""
    # 檢查權限：只有管理員可以操作
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': '權限不足：只有管理員可以執行出庫操作'}), 403

    try:
        data = request.get_json()
        part_name = data.get('part_name')
        work_order = data.get('work_order')
        quantity = data.get('quantity')
        model = data.get('model')
        
        if not part_name or not work_order or not quantity:
            return jsonify({'success': False, 'error': '缺少必要參數'}), 400
        
        # 調用 inventory.py 中的出庫函數
        from ..models.inventory import stock_out_product
        result = stock_out_product(part_name, work_order, quantity, model)
        
        if result['success']:
            # 通知所有客戶端更新數據
            socketio.emit('data_updated', {'type': 'stock_out', 'part': part_name, 'work_order': work_order})
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

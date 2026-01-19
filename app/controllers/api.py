from flask import Blueprint, jsonify
from datetime import datetime
from ..models.inventory import load_casting_inventory
from ..models.order import load_orders

api_bp = Blueprint('api', __name__)

def calculate_supply_demand():
    """計算供需狀況"""
    inventory = load_casting_inventory()
    orders = load_orders()
    
    supply = inventory.get('summary', {})
    demand = orders.get('demand', {})
    
    analysis = []
    for part in ['底座', '工作台', '橫樑', '立柱']:
        stock = supply.get(part, 0)
        need = demand.get(part, 0)
        diff = stock - need
        status = '充足' if diff >= 0 else '不足'
        analysis.append({
            '鑄件': part, '庫存': stock, '需求': need, '差異': diff, '狀態': status
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
def api_summary():
    inventory = load_casting_inventory()
    orders = load_orders()
    supply_demand = calculate_supply_demand()
    
    return jsonify({
        'inventory': inventory.get('summary', {}),
        'inventory_details': inventory.get('details', []),
        'orders_stats': orders.get('stats', {}),
        'supply_demand': supply_demand,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

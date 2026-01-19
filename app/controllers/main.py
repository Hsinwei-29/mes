from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """主頁面 - 庫存看板"""
    return render_template('main/index.html')

@main_bp.route('/orders')
def orders_page():
    """工單需求頁面"""
    return render_template('main/orders.html')

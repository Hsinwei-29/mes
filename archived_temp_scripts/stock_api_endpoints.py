@api_bp.route('/stock/in', methods=['POST'])
def stock_in():
    """入庫 API - 增加素材數量"""
    try:
        data = request.get_json()
        part_name = data.get('part_name')
        quantity = data.get('quantity')
        
        if not part_name or not quantity:
            return jsonify({'success': False, 'error': '缺少必要參數'}), 400
        
        # 調用 inventory.py 中的入庫函數
        from ..models.inventory import stock_in_material
        result = stock_in_material(part_name, quantity)
        
        if result['success']:
            # 通知所有客戶端更新數據
            socketio.emit('data_updated', {'type': 'stock_in', 'part': part_name})
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/stock/out', methods=['POST'])
def stock_out():
    """出庫 API - 扣除成品數量"""
    try:
        data = request.get_json()
        part_name = data.get('part_name')
        work_order = data.get('work_order')
        quantity = data.get('quantity')
        
        if not part_name or not work_order or not quantity:
            return jsonify({'success': False, 'error': '缺少必要參數'}), 400
        
        # 調用 inventory.py 中的出庫函數
        from ..models.inventory import stock_out_product
        result = stock_out_product(part_name, work_order, quantity)
        
        if result['success']:
            # 通知所有客戶端更新數據
            socketio.emit('data_updated', {'type': 'stock_out', 'part': part_name, 'work_order': work_order})
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

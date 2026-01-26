from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    """管理員權限裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': '需要管理員權限'}), 403
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登入頁面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.get_by_username(username)
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('使用者名稱或密碼錯誤', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """管理員控制台"""
    users = User.load_all()
    return render_template('admin/dashboard.html', users=users)

@auth_bp.route('/admin/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """取得使用者列表 API"""
    users = User.load_all()
    return jsonify({
        'users': [{'id': u.id, 'username': u.username, 'role': u.role, 'created_at': u.created_at} for u in users]
    })

@auth_bp.route('/admin/users', methods=['POST'])
@login_required
@admin_required
def create_user():
    """新增使用者 API"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    
    if not username or not password:
        return jsonify({'error': '使用者名稱和密碼為必填'}), 400
    
    user = User.create(username, password, role)
    
    if user:
        return jsonify({'success': True, 'user': {'id': user.id, 'username': user.username, 'role': user.role}})
    else:
        return jsonify({'error': '使用者名稱已存在'}), 400

@auth_bp.route('/admin/users/<user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """刪除使用者 API"""
    if user_id == current_user.id:
        return jsonify({'error': '無法刪除自己的帳戶'}), 400
    
    users = User.load_all()
    users = [u for u in users if u.id != user_id]
    User.save_all(users)
    
    return jsonify({'success': True})

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """個人資料頁面"""
    return render_template('auth/profile.html')

@auth_bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密碼 API"""
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': '請填寫所有欄位'}), 400
    
    # 驗證當前密碼
    if not current_user.check_password(current_password):
        return jsonify({'error': '當前密碼錯誤'}), 400
    
    # 更新密碼
    users = User.load_all()
    for user in users:
        if user.id == current_user.id:
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(new_password)
            break
    
    User.save_all(users)
    return jsonify({'success': True, 'message': '密碼已更新'})

@auth_bp.route('/profile/change-username', methods=['POST'])
@login_required
def change_username():
    """修改使用者名稱 API"""
    data = request.get_json()
    new_username = data.get('new_username')
    
    if not new_username:
        return jsonify({'error': '請輸入新的使用者名稱'}), 400
    
    # 檢查使用者名稱是否已存在
    if User.get_by_username(new_username):
        return jsonify({'error': '使用者名稱已存在'}), 400
    
    # 更新使用者名稱
    users = User.load_all()
    for user in users:
        if user.id == current_user.id:
            user.username = new_username
            break
    
    User.save_all(users)
    return jsonify({'success': True, 'message': '使用者名稱已更新'})

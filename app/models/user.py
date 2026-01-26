from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime

class User(UserMixin):
    def __init__(self, id, username, password_hash, role='user', created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.now().isoformat()
    
    def check_password(self, password):
        """驗證密碼"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """檢查是否為管理員"""
        return self.role == 'admin'
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at
        }
    
    @staticmethod
    def get_users_file():
        """取得使用者檔案路徑"""
        return 'users.json'
    
    @staticmethod
    def load_all():
        """載入所有使用者"""
        users_file = User.get_users_file()
        if not os.path.exists(users_file):
            # 建立預設管理員帳戶
            User.init_default_users()
        
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [User(**u) for u in data.get('users', [])]
        except:
            return []
    
    @staticmethod
    def get_by_id(user_id):
        """根據 ID 取得使用者"""
        users = User.load_all()
        for user in users:
            if user.id == user_id:
                return user
        return None
    
    @staticmethod
    def get_by_username(username):
        """根據使用者名稱取得使用者"""
        users = User.load_all()
        for user in users:
            if user.username == username:
                return user
        return None
    
    @staticmethod
    def create(username, password, role='user'):
        """建立新使用者"""
        users = User.load_all()
        
        # 檢查使用者名稱是否已存在
        if User.get_by_username(username):
            return None
        
        # 生成新 ID
        new_id = str(max([int(u.id) for u in users], default=0) + 1)
        
        # 建立新使用者
        password_hash = generate_password_hash(password)
        new_user = User(new_id, username, password_hash, role)
        
        # 儲存
        users.append(new_user)
        User.save_all(users)
        
        return new_user
    
    @staticmethod
    def save_all(users):
        """儲存所有使用者"""
        users_file = User.get_users_file()
        data = {'users': [u.to_dict() for u in users]}
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def init_default_users():
        """初始化預設使用者"""
        admin = User('1', 'admin', generate_password_hash('admin123'), 'admin')
        User.save_all([admin])
        print("已建立預設管理員帳戶: admin / admin123")

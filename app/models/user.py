from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import threading
from datetime import datetime

# ── 記憶體快取，避免每次 user_loader 都重讀 JSON ──────────────────
_users_cache = None          # List[User] 或 None
_cache_lock  = threading.Lock()
_FAST_METHOD = 'pbkdf2:sha256:260000'  # 比 scrypt 快 10-20 倍，仍安全

def _invalidate_cache():
    """寫入 users.json 後呼叫，清除快取使下次讀取重新載入"""
    global _users_cache
    with _cache_lock:
        _users_cache = None

class User(UserMixin):
    def __init__(self, id, username, password_hash, role='user', created_at=None, chinese_name=''):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.now().isoformat()
        self.chinese_name = chinese_name
    
    def check_password(self, password):
        """驗證密碼；若使用舊式 scrypt hash，驗證成功後自動遷移至較快的 pbkdf2"""
        if not check_password_hash(self.password_hash, password):
            return False
        # 自動遷移：scrypt 很慢，改成 pbkdf2:sha256 後下次登入快很多
        if self.password_hash.startswith('scrypt:'):
            try:
                new_hash = generate_password_hash(password, method=_FAST_METHOD)
                # 直接更新 JSON，不透過 save_all 以降低耦合
                users = User.load_all(force=True)
                for u in users:
                    if u.id == self.id:
                        u.password_hash = new_hash
                        break
                User.save_all(users)
                self.password_hash = new_hash  # 同步更新當前實例
                print(f"[AUTH] 已將使用者 {self.username} 的密碼 hash 遷移至 pbkdf2")
            except Exception as e:
                print(f"[AUTH] 密碼遷移失敗（不影響登入）: {e}")
        return True
    
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
            'created_at': self.created_at,
            'chinese_name': self.chinese_name
        }
    
    @staticmethod
    def get_users_file():
        """取得使用者檔案路徑"""
        return 'users.json'
    
    @staticmethod
    def load_all(force=False):
        """載入所有使用者（有記憶體快取，避免重複 I/O）"""
        global _users_cache
        if not force:
            with _cache_lock:
                if _users_cache is not None:
                    return list(_users_cache)  # 回傳淺複製
        users_file = User.get_users_file()
        if not os.path.exists(users_file):
            User.init_default_users()
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                users = [User(**u) for u in data.get('users', [])]
            with _cache_lock:
                _users_cache = list(users)
            return users
        except Exception as e:
            print(f"[USER] load_all 失敗: {e}")
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
    def create(username, password, role='user', chinese_name=''):
        """建立新使用者"""
        users = User.load_all()
        
        # 檢查使用者名稱是否已存在
        if User.get_by_username(username):
            return None
        
        # 生成新 ID
        new_id = str(max([int(u.id) for u in users], default=0) + 1)
        
        # 建立新使用者
        password_hash = generate_password_hash(password, method=_FAST_METHOD)
        new_user = User(new_id, username, password_hash, role, chinese_name=chinese_name)
        
        # 儲存
        users.append(new_user)
        User.save_all(users)
        
        return new_user
    
    @staticmethod
    def save_all(users):
        """儲存所有使用者並清除快取"""
        users_file = User.get_users_file()
        data = {'users': [u.to_dict() for u in users]}
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        _invalidate_cache()  # 寫入後強制下次重讀
    
    @staticmethod
    def get_name_map():
        """取得 使用者名稱 -> 中文名字 的對照表"""
        users = User.load_all()
        return {u.username: (u.chinese_name if (hasattr(u, 'chinese_name') and u.chinese_name) else u.username) for u in users}

    @staticmethod
    def init_default_users():
        """初始化預設使用者（使用較快的 pbkdf2 hash）"""
        admin = User('1', 'admin', generate_password_hash('admin123', method=_FAST_METHOD), 'admin')
        User.save_all([admin])
        print("已建立預設管理員帳戶: admin / admin123")

# auth.py
"""
Kullanıcı kimlik doğrulama, yetkilendirme ve oturum yönetimi ile ilgili tüm fonksiyonları içerir.
"""
import json
import logging
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

from config import USERS_DB_PATH

class User(UserMixin):
    """Flask-Login için Kullanıcı sınıfı"""
    def __init__(self, id: str, role: str):
        self.id = id
        self.role = role

def _load_users_from_db() -> dict:
    """
    Kullanıcı veritabanını (users.json) okur.
    Eğer dosya yoksa, varsayılan admin ve user kullanıcılarını oluşturur.
    """
    try:
        with open(USERS_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"'{USERS_DB_PATH}' bulunamadı. Varsayılan kullanıcılar oluşturuluyor (admin/admin, user/user).")
        # pbkdf2:sha256, güvenli bir hashleme yöntemidir.
        hashed_admin_pass = generate_password_hash("admin", method='pbkdf2:sha256')
        hashed_user_pass = generate_password_hash("user", method='pbkdf2:sha256')
        
        default_users = {
            "admin": {"password_hash": hashed_admin_pass, "role": "admin"},
            "user": {"password_hash": hashed_user_pass, "role": "user"}
        }
        
        with open(USERS_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, indent=4)
        return default_users
    except json.JSONDecodeError:
        logging.error(f"'{USERS_DB_PATH}' dosyası bozuk veya geçersiz JSON formatında.")
        return {}

def load_user(user_id: str) -> User or None:
    """
    Flask-Login'in user_loader'ı tarafından kullanılır.
    Verilen kullanıcı ID'sine karşılık gelen User nesnesini döndürür.
    """
    users = _load_users_from_db()
    user_data = users.get(user_id)
    if user_data:
        return User(id=user_id, role=user_data.get('role', 'user'))
    return None

def verify_user(username: str, password: str) -> User or None:
    """
    Kullanıcı adı ve şifreyi doğrular.
    Başarılı ise User nesnesini, değilse None döndürür.
    """
    users = _load_users_from_db()
    user_data = users.get(username)
    if user_data and check_password_hash(user_data.get('password_hash', ''), password):
        return User(id=username, role=user_data.get('role', 'user'))
    return None
# FILE: utils.py
import json
import os
import hashlib

USER_FILE = "users.json"

# --- 1. HÀM MÃ HÓA MẬT KHẨU (Bảo mật cơ bản) ---
def make_hashes(password):
    """Biến mật khẩu thành chuỗi mã hóa SHA256"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    """Kiểm tra mật khẩu nhập vào có khớp với mã hóa không"""
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- 2. QUẢN LÝ DỮ LIỆU NGƯỜI DÙNG ---
def load_users():
    """Đọc danh sách user từ file json"""
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {}

def save_user(username, password, name):
    """Lưu user mới vào file"""
    users = load_users()
    if username in users:
        return False, "Tài khoản đã tồn tại!"
    
    users[username] = {
        "password": make_hashes(password),
        "name": name,
        "created_at": "today"
    }
    
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    return True, "Đăng ký thành công!"

def authenticate(username, password):
    """Xác thực đăng nhập"""
    users = load_users()
    if username not in users:
        return False, "Tài khoản không tồn tại."
    
    if check_hashes(password, users[username]["password"]):
        return True, users[username]["name"] # Trả về Tên hiển thị
    else:
        return False, "Sai mật khẩu."
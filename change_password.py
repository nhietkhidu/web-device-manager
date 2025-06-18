import sqlite3
from werkzeug.security import generate_password_hash

# Thông tin cần cập nhật
username = 'admin1'
new_password = '123456'  # Đổi thành mật khẩu bạn muốn

# Kết nối đến CSDL
conn = sqlite3.connect('device.db')
cursor = conn.cursor()

# Băm mật khẩu mới
hashed_password = generate_password_hash(new_password)

# Cập nhật vào bảng users
cursor.execute("UPDATE users SET password=? WHERE username=?", (hashed_password, username))
conn.commit()
conn.close()

print(f"✅ Mật khẩu mới cho tài khoản '{username}' đã được cập nhật.")

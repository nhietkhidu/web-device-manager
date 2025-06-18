import sqlite3
from werkzeug.security import generate_password_hash

DB_FILE = 'device.db'

# 1. Kết nối đến file database mới
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# 2. Tạo bảng users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

# 3. Tạo bảng devices
cursor.execute('''
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT,
    name TEXT,
    specs TEXT,
    category TEXT,
    manufacturer TEXT,
    year TEXT,
    date_in_use TEXT,
    status TEXT,
    location TEXT,
    link TEXT,
    stage TEXT
)
''')

# 4. Tạo bảng maintenance_history
cursor.execute('''
CREATE TABLE IF NOT EXISTS maintenance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER,
    date TEXT,
    content TEXT,
    performed_by TEXT,
    FOREIGN KEY (device_id) REFERENCES devices(id)
)
''')

# 5. Thêm tài khoản người dùng mẫu
cursor.execute("DELETE FROM users")
cursor.executemany('''
INSERT INTO users (username, password, role)
VALUES (?, ?, ?)
''', [
    ('admin1', generate_password_hash('123'), 'admin'),
    ('viewer1', generate_password_hash('123'), 'viewer')
])

# 6. Thêm thiết bị mẫu
cursor.execute("DELETE FROM devices")
cursor.executemany('''
INSERT INTO devices (code, name, specs, category, manufacturer, year, date_in_use, status, location, link, stage)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', [
    ('R11BD01', 'Van đóng mở cấp khí nóng', 'abc', 'a', 'ab', '2025', '2025-05-20', 'ok', '1', 'https://google.com', 'R11 Nồi hơi SP'),
    ('R11BD02', 'Van đóng mở cấp khí nóng', 'abc', 'a', 'ab', '2025', '2025-05-20', 'ok', '2', 'https://google.com', 'R51 Xử lý nước'),
    ('PLC01', 'PLC điều khiển', 'abc', 'a', 'ab', '2025', '2025-05-20', 'ok', 'Nhà tua bin', 'https://google.com', 'PLC')
])

# 7. Thêm lịch sử bảo dưỡng mẫu
cursor.execute("DELETE FROM maintenance_history")
cursor.executemany('''
INSERT INTO maintenance_history (device_id, date, content, performed_by)
VALUES (?, ?, ?, ?)
''', [
    (1, '2025-01-10', 'Bảo dưỡng định kỳ', 'Kỹ thuật A'),
    (1, '2025-05-12', 'Thay thế van khí', 'Kỹ thuật B'),
    (2, '2025-04-01', 'Kiểm tra cảm biến áp suất', 'Kỹ thuật C'),
    (3, '2025-03-18', 'Vệ sinh bộ lọc', 'Kỹ thuật D')
])

# 8. Lưu thay đổi và đóng kết nối
conn.commit()
conn.close()

print("✅ Đã tạo file device.db với dữ liệu mẫu thành công.")

import sqlite3

DB_FILE = 'device.db'

# Kết nối đến cơ sở dữ liệu
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Tạo bảng maintenance_history nếu chưa có
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

# Xoá dữ liệu cũ nếu bạn muốn reset:
cursor.execute('DELETE FROM maintenance_history')

# Dữ liệu mẫu (device_id phải đúng với thiết bị bạn đã có)
sample_data = [
    (1, '2025-01-10', 'Bảo dưỡng định kỳ', 'Kỹ thuật A'),
    (1, '2025-05-12', 'Thay thế van khí', 'Kỹ thuật B'),
    (2, '2025-04-01', 'Kiểm tra cảm biến áp suất', 'Kỹ thuật C'),
    (3, '2025-03-18', 'Vệ sinh bộ lọc', 'Kỹ thuật D')
]

cursor.executemany('''
INSERT INTO maintenance_history (device_id, date, content, performed_by)
VALUES (?, ?, ?, ?)
''', sample_data)

# Lưu thay đổi

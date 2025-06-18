import sqlite3

# Kết nối đến hoặc tạo mới cơ sở dữ liệu SQLite
conn = sqlite3.connect('device.db')  # device.db là tên file cơ sở dữ liệu
cursor = conn.cursor()

# Tạo bảng devices để lưu thông tin thiết bị
cursor.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        specs TEXT,
        category TEXT,
        manufacturer TEXT,
        year INTEGER,
        date_in_use TEXT,
        status TEXT,
        location TEXT,
        link TEXT,
        stage TEXT
    )
''')

# Tạo bảng maintenance_history để lưu lịch sử bảo dưỡng
cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER,
        maintenance_date TEXT,
        description TEXT,
        FOREIGN KEY (device_id) REFERENCES devices(id)
    )
''')

# Tạo bảng users để quản lý người dùng đăng nhập
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')

# Commit các thay đổi và đóng kết nối
conn.commit()
conn.close()

print("Cơ sở dữ liệu đã được tạo thành công.")

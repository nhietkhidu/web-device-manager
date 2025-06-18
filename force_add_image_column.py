import sqlite3

conn = sqlite3.connect("device.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE maintenance_history ADD COLUMN image_filename TEXT;")
    print(">> Đã thêm cột 'image_filename' vào bảng maintenance_history.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print(">> Cột 'image_filename' đã tồn tại.")
    else:
        raise
finally:
    conn.commit()
    conn.close()

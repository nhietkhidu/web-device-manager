import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os

# Kết nối đến SQLite
sqlite_conn = sqlite3.connect("device.db")
sqlite_cursor = sqlite_conn.cursor()

# Đọc dữ liệu từ SQLite
sqlite_cursor.execute("SELECT * FROM devices")
rows = sqlite_cursor.fetchall()

# Lấy tên cột từ bảng SQLite
columns = [description[0] for description in sqlite_cursor.description]

# Làm sạch dữ liệu (chuyển None và kiểu phù hợp)
cleaned_rows = []
for row in rows:
    cleaned_row = []
    for i, val in enumerate(row):
        col = columns[i]
        if col == "year":
            try:
                cleaned_row.append(int(val))
            except:
                cleaned_row.append(None)
        elif col == "location":
            cleaned_row.append(str(val) if val is not None else None)
        else:
            cleaned_row.append(val)
    cleaned_rows.append(tuple(cleaned_row))

# Kết nối đến PostgreSQL
pg_conn = psycopg2.connect(
    dbname="device_db_neap",
    user="device_db_neap_user",
    password="tynNT9JS0XDLdbxWvgzyvRiKY4Gy3Czt",
    host="dpg-d18nsah5pdvs73co69t0-a.oregon-postgres.render.com",
    port="5432"
)
pg_cursor = pg_conn.cursor()

# Tạo bảng nếu chưa có (sửa lại schema nếu cần)
create_table_sql = """
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    code TEXT,
    name TEXT,
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
"""
pg_cursor.execute(create_table_sql)
pg_conn.commit()

# Xoá dữ liệu cũ nếu muốn
pg_cursor.execute("DELETE FROM devices")
pg_conn.commit()

# Chèn dữ liệu
insert_sql = f"INSERT INTO devices ({', '.join(columns)}) VALUES %s"
execute_values(pg_cursor, insert_sql, cleaned_rows)
pg_conn.commit()

# Đóng kết nối
sqlite_conn.close()
pg_cursor.close()
pg_conn.close()

print("✔️ Dữ liệu đã chuyển thành công từ SQLite sang PostgreSQL.")

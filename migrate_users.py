import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# Kết nối đến SQLite
sqlite_conn = sqlite3.connect("device.db")
sqlite_cur = sqlite_conn.cursor()

# Kết nối đến PostgreSQL
pg_conn = psycopg2.connect(
    "postgresql://device_db_neap_user:tynNT9JS0XDLdbxWvgzyvRiKY4Gy3Czt@dpg-d18nsah5pdvs73co69t0-a.oregon-postgres.render.com/device_db_neap"
)
pg_cur = pg_conn.cursor()

# Tạo bảng users nếu chưa có
pg_cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);
""")
pg_conn.commit()

# Đọc dữ liệu từ SQLite
sqlite_cur.execute("SELECT id, username, password, role FROM users")
rows = sqlite_cur.fetchall()

# Ghi dữ liệu sang PostgreSQL (bỏ qua nếu id đã tồn tại)
insert_sql = "INSERT INTO users (id, username, password, role) VALUES %s ON CONFLICT (id) DO NOTHING"
execute_values(pg_cur, insert_sql, rows)

pg_conn.commit()
sqlite_conn.close()
pg_conn.close()

print("✅ Đã chuyển dữ liệu bảng users thành công.")

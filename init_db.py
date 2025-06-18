import sqlite3

conn = sqlite3.connect('device.db')
cursor = conn.cursor()

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

conn.commit()
conn.close()
print("Đã tạo xong device.db")
def init_users():
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                     ('admin1', generate_password_hash('123'), 'admin'))
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                     ('viewer1', generate_password_hash('123'), 'viewer'))
        conn.commit()
    except:
        pass
    conn.close()

init_users()

import sqlite3

conn = sqlite3.connect('device.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

c.execute("INSERT INTO users (username, password, role) VALUES ('admin', '123', 'admin')")
c.execute("INSERT INTO users (username, password, role) VALUES ('viewer', '123', 'viewer')")

conn.commit()
conn.close()
print("Done.")

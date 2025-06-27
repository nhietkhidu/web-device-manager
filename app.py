from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename

import sqlite3
import os
import zipfile
from io import BytesIO
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DB_FILE = 'device.db'

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_stages():
    return [
        'R11 Nồi hơi SP', 'R21 Nồi hơi AQC', 'R31 Tua Bin',
        'R51 Xử lý nước', 'S41 S71 Bơm cấp nước', 'S61 Tháp giải nhiệt', 'PLC', 'Thiết bị chung'
    ]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Xử lý ảnh upload
        image_file = request.files.get('image_file')
        image_link = request.form.get('image_link')
        image_name = None

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, filename)
            image_file.save(save_path)
            image_name = filename
        elif image_link:
            image_name = image_link.strip()

        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user'] = dict(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Sai tài khoản hoặc mật khẩu')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/devices')

@app.route('/')
@app.route('/devices')
def index():
    user = session.get('user')  # Cho phép truy cập không cần đăng nhập

    stage = request.args.get('stage')
    selected_id = request.args.get('selected_id')
    conn = get_db()

    query = "SELECT * FROM devices WHERE 1=1"
    params = []

    for field in ['code', 'name', 'status', 'year']:
        value = request.args.get(field)
        if value:
            query += f" AND {field} LIKE ?"
            params.append(f"%{value}%")

    if stage:
        query += " AND stage = ?"
        params.append(stage)

    query += " ORDER BY id DESC LIMIT 1000"

    devices = conn.execute(query, tuple(params)).fetchall()
    conn.close()

    return render_template('index.html',
                           devices=devices,
                           stages=get_stages(),
                           selected_stage=stage,
                           selected_id=selected_id,
                           user=user)


@app.route('/add', methods=['GET', 'POST'])
def add_device():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Xử lý ảnh upload
        image_file = request.files.get('image_file')
        image_link = request.form.get('image_link')
        image_name = None

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, filename)
            image_file.save(save_path)
            image_name = filename
        elif image_link:
            image_name = image_link.strip()

        data = request.form
        conn = get_db()
        conn.execute("""INSERT INTO devices (code, name, specs, category, manufacturer, year, date_in_use, status, location, link, stage)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (data['code'], data['name'], data['specs'], data['category'], data['manufacturer'], data['year'],
                      data['date_in_use'], data['status'], data['location'], data['link'], data['stage']))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html', stages=get_stages())

@app.route('/edit', methods=['POST'])
def edit_device():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))
    selected_id = request.form.get('selected_id')
    if not selected_id:
        return redirect(url_for('index'))
    conn = get_db()
    device = conn.execute('SELECT * FROM devices WHERE id = ?', (selected_id,)).fetchone()
    conn.close()
    return render_template('edit_device.html', device=device, stages=get_stages())

@app.route('/update', methods=['POST'])
def update_device():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))
    data = request.form
    conn = get_db()
    conn.execute("""UPDATE devices SET code=?, name=?, specs=?, category=?, manufacturer=?, year=?, date_in_use=?,
                    status=?, location=?, link=?, stage=? WHERE id=?""",
                 (data['code'], data['name'], data['specs'], data['category'], data['manufacturer'], data['year'],
                  data['date_in_use'], data['status'], data['location'], data['link'], data['stage'], data['id']))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete_device():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))
    selected_id = request.form.get('selected_id')
    if selected_id:
        conn = get_db()
        conn.execute('DELETE FROM devices WHERE id = ?', (selected_id,))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/export_excel')
def export_excel():
    user = session.get('user')  # Cho phép truy cập không cần đăng nhập
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM devices", conn)
    df = df.rename(columns={
        'id': 'ID',
        'code': 'Mã thiết bị',
        'name': 'Tên thiết bị',
        'specs': 'Thông số kỹ thuật',
        'category': 'Loại',
        'manufacturer': 'Hãng',
        'year': 'Năm SX',
        'date_in_use': 'Ngày sử dụng',
        'status': 'Tình trạng',
        'location': 'Vị trí',
        'link': 'Link tài liệu',
        'stage': 'Công đoạn'
    })
    conn.close()
    file_path = 'devices_export.xlsx'
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

@app.route('/maintenance_all')
def maintenance_all():
    user = session.get('user')  # Cho phép truy cập không cần đăng nhập

    keyword = request.args.get('q', '').strip()

    conn = get_db()
    query = '''
        SELECT mh.id, mh.date, mh.content, mh.performed_by, mh.image_filename,
               d.code AS device_code, d.name AS device_name, d.stage AS device_stage
        FROM maintenance_history mh
        JOIN devices d ON mh.device_id = d.id
    '''
    params = []

    if keyword:
        query += '''
            WHERE
                d.code LIKE ? OR
                d.name LIKE ? OR
                d.stage LIKE ? OR
                mh.content LIKE ?
        '''
        like_kw = f'%{keyword}%'
        params = [like_kw, like_kw, like_kw, like_kw]

    query += ' ORDER BY mh.date DESC'

    history = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('maintenance_all.html', history=history, keyword=keyword, user=user)
@app.route('/maintenance_add', methods=['GET', 'POST'])
def maintenance_add():
    user = session.get('user')  # Cho phép truy cập không cần đăng nhập

    conn = get_db()

    if request.method == 'POST':
        # Xử lý ảnh upload
        image_file = request.files.get('image_file')
        image_link = request.form.get('image_link')
        image_name = None

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, filename)
            image_file.save(save_path)
            image_name = filename
        elif image_link:
            image_name = image_link.strip()

        device_id = request.form['device_id']
        date = request.form['date']
        content = request.form['content']
        performed_by = request.form['performed_by']

        conn.execute("""
            INSERT INTO maintenance_history (device_id, date, content, performed_by, image_filename)
            VALUES (?, ?, ?, ?, ?)
        """, (device_id, date, content, performed_by, image_name))
        conn.commit()
        conn.close()
        return redirect(url_for('maintenance_all'))

    devices = conn.execute("SELECT id, code, name FROM devices").fetchall()
    conn.close()
    return render_template('maintenance_add.html', devices=devices)
@app.route('/maintenance_edit/<int:id>', methods=['GET', 'POST'])
def maintenance_edit(id):
    user = session.get('user')  # Cho phép truy cập không cần đăng nhập
    conn = get_db()

    if request.method == 'POST':
        # Xử lý ảnh upload
        image_file = request.files.get('image_file')
        image_link = request.form.get('image_link')
        image_name = None

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, filename)
            image_file.save(save_path)
            image_name = filename
        elif image_link:
            image_name = image_link.strip()

        device_id = request.form['device_id']
        date = request.form['date']
        content = request.form['content']
        performed_by = request.form['performed_by']

        conn.execute('''
            UPDATE maintenance_history
            SET device_id=?, date=?, content=?, performed_by=?
            WHERE id=?
        ''', (device_id, date, content, performed_by, id))
        conn.commit()
        conn.close()
        return redirect(url_for('maintenance_all'))

    devices = conn.execute("SELECT id, code, name FROM devices").fetchall()
    history = conn.execute("SELECT * FROM maintenance_history WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template('maintenance_edit.html', history=history, devices=devices)

@app.route('/maintenance_delete/<int:id>', methods=['POST'])
def maintenance_delete(id):
    user = session.get('user')  # Cho phép truy cập không cần đăng nhập
    conn = get_db()
    conn.execute("DELETE FROM maintenance_history WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('maintenance_all'))
def init_users():
    conn = get_db()
    user_exists = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_exists == 0:
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                     ('admin1', generate_password_hash('123'), 'admin'))
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                     ('viewer1', generate_password_hash('123'), 'viewer'))
        conn.commit()
    conn.close()
@app.route('/device/<int:device_id>/history')
def device_history(device_id):
    conn = get_db()
    device = conn.execute('SELECT * FROM devices WHERE id = ?', (device_id,)).fetchone()
    history = conn.execute('SELECT * FROM maintenance_history WHERE device_id = ? ORDER BY date DESC', (device_id,)).fetchall()
    conn.close()
    return render_template('maintenance_history.html', device=device, history=history)
@app.route('/download-db')
def download_db():
    if 'user' not in session or session['user']['role'] != 'admin':
        return "Bạn không có quyền truy cập.", 403

    db_path = os.path.join(os.getcwd(), 'device.db')
    return send_file(db_path, as_attachment=True)
@app.route('/download-backup')
def download_backup():
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Thêm database
        db_path = os.path.join(os.getcwd(), 'device.db')  # đúng tên file DB
        if os.path.exists(db_path):
            zf.write(db_path, arcname='device.db')
        
        # Thêm thư mục ảnh
        upload_folder = os.path.join('static', 'uploads')
        for root, dirs, files in os.walk(upload_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')  # giữ cấu trúc thư mục
                zf.write(file_path, arcname)

    memory_file.seek(0)
    return send_file(memory_file, download_name='backup_all.zip', as_attachment=True)
if __name__ == '__main__':
    init_users()
    app.run(host='0.0.0.0', port=8089, debug=True)



@app.route('/edit/<int:id>', methods=['GET'])
def show_edit_device(id):
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    device = conn.execute('SELECT * FROM devices WHERE id=?', (id,)).fetchone()
    conn.close()
    return render_template('edit_device.html', device=device, stages=get_stages())




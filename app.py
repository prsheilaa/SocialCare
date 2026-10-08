from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# Fungsi koneksi ke database XAMPP
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="sosialcare_db"
    )

@app.route('/')
def dashboard():
    # 1. Buka koneksi ke database sosialcare_db
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # 2. Ambil data komentar dari tabel ig_comments
    cursor.execute("SELECT username, comment_text, created_at FROM ig_comments ORDER BY created_at DESC")
    comments_data = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    # 3. Format data agar cocok dengan variabel template HTML (`antrian`)
    antrian = []
    for row in comments_data:
        antrian.append({
            'penulis': row['username'],
            'isi': row['comment_text'],
            'akun': {'platform': 'Instagram'},
            'prioritas': 'baru',       # Kelas CSS tag prioritas
            'status': 'baru',          # Kelas CSS tag status
            'waktu': row['created_at']
        })
        
    # Hitung total komentar baru untuk bagian KPI di dashboard
    n_baru = len(antrian)
    
    # Data dummy sementara untuk variabel lain agar tidak error di template
    context = {
        'salam': 'Selamat bekerja',
        'user': {'first_name': 'Petugas', 'username': 'petugas'},
        'n_baru': n_baru,
        'n_analisis': 0,
        'n_menunggu': 0,
        'n_siap': 0,
        'n_selesai': 0,
        'antrian': antrian,
        'siap': [],
        'request_saya': []
    }

    # Render ke file HTML dashboard Anda
    return render_template('dashboard.html', **context)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
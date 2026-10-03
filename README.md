cat > README.md <<'EOF'
# Monitoring Komentar Sosial Media - PLN NP UP Paiton

Website Django untuk memantau dan menindaklanjuti komentar sosial media perusahaan.
Peran: Administrator dan Petugas.

## Cara menjalankan
1. `git clone <url-repo>` lalu `cd` ke foldernya
2. `python -m venv env`
3. `source env/Scripts/activate` (Git Bash di Windows)
4. `pip install -r requirements.txt`
5. `python manage.py migrate`
6. `python manage.py createsuperuser` (akun Administrator)
7. `python manage.py seed_demo` (data contoh, hanya untuk pengembangan)
8. `python manage.py runserver`

Akun Petugas contoh dari seed_demo: `petugas1` / `petugas123` (hanya untuk pengembangan).

## Status
- [x] Login, logout, dashboard Administrator dan Petugas
- [ ] Halaman komentar, persetujuan request, laporan, kelola data
EOF
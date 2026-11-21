# Praktikum SOA - Sistem Informasi Manajemen Rumah Sakit

## Arsitektur
- Server A (`server_a_web`): UI Flask di port 5000.
- Server B (`server_b_api`): REST API Flask + MySQL di port 5001.
- Komunikasi antarserver menggunakan HTTP dan JSON.

## Instalasi
1. Jalankan MySQL melalui XAMPP.
2. Buka phpMyAdmin, impor `database/rumah_sakit.sql`.
3. Salin `.env.example` menjadi `.env`, sesuaikan konfigurasi MySQL.
4. Di terminal folder proyek: `python -m venv venv`
5. Aktifkan: Windows `venv\Scripts\activate`; macOS/Linux `source venv/bin/activate`
6. `pip install -r requirements.txt`

## Membuat akun demo
Setelah impor SQL, dari folder `server_b_api` jalankan sekali:
`python seed_demo.py`
Script ini membuat akun demo dan data awal (poliklinik, dokter, pasien) bila belum ada.

## Menjalankan (dua terminal VS Code)
Terminal 1:
`cd server_b_api`
`python app.py`
Server B: http://127.0.0.1:5001

Terminal 2:
`cd server_a_web`
`python app.py`
Server A: http://127.0.0.1:5000

## Akun demo
admin / admin123
dokter / dokter123
petugas / petugas123
pasien / pasien123

## Endpoint
POST `/api/login`, GET `/api/me`
GET/POST `/api/<resource>`
PUT/DELETE `/api/<resource>/<id>`
GET `/api/reports/summary`
GET `/api/reports/patients`

Resource: poliklinik, pengguna, dokter, pasien, asuransi, pendaftaran.
Semua endpoint selain login memerlukan `Authorization: Bearer <token>`.
RBAC diperiksa pada Server B. Penghapusan data dibatasi untuk admin.

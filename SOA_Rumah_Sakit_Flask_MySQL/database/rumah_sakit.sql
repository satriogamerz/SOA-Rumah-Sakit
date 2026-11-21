CREATE DATABASE IF NOT EXISTS rumah_sakit CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE rumah_sakit;
CREATE TABLE poliklinik (
 id INT AUTO_INCREMENT PRIMARY KEY, nama_poliklinik VARCHAR(100) NOT NULL,
 lokasi VARCHAR(150), keterangan TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE pengguna (
 id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL, nama_lengkap VARCHAR(120) NOT NULL,
 role ENUM('admin','dokter','petugas','pasien') NOT NULL DEFAULT 'pasien',
 email VARCHAR(120), aktif TINYINT(1) DEFAULT 1,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE dokter (
 id INT AUTO_INCREMENT PRIMARY KEY, pengguna_id INT NOT NULL UNIQUE,
 poliklinik_id INT, no_sip VARCHAR(60), spesialisasi VARCHAR(100), no_telepon VARCHAR(25),
 FOREIGN KEY(pengguna_id) REFERENCES pengguna(id) ON DELETE CASCADE,
 FOREIGN KEY(poliklinik_id) REFERENCES poliklinik(id) ON DELETE SET NULL
);
CREATE TABLE asuransi (
 id INT AUTO_INCREMENT PRIMARY KEY, nama_asuransi VARCHAR(120) NOT NULL,
 jenis VARCHAR(80), nomor_kontak VARCHAR(30), keterangan TEXT
);
CREATE TABLE pasien (
 id INT AUTO_INCREMENT PRIMARY KEY, pengguna_id INT NOT NULL UNIQUE,
 no_rm VARCHAR(30) NOT NULL UNIQUE, tanggal_lahir DATE,
 jenis_kelamin ENUM('L','P'), alamat TEXT, no_telepon VARCHAR(25),
 asuransi_id INT, no_peserta VARCHAR(60),
 FOREIGN KEY(pengguna_id) REFERENCES pengguna(id) ON DELETE CASCADE,
 FOREIGN KEY(asuransi_id) REFERENCES asuransi(id) ON DELETE SET NULL
);
CREATE TABLE pendaftaran (
 id INT AUTO_INCREMENT PRIMARY KEY, pasien_id INT NOT NULL, dokter_id INT,
 poliklinik_id INT NOT NULL, tanggal_kunjungan DATE NOT NULL, keluhan TEXT,
 status ENUM('Menunggu','Diperiksa','Selesai','Batal') DEFAULT 'Menunggu',
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(pasien_id) REFERENCES pasien(id) ON DELETE CASCADE,
 FOREIGN KEY(dokter_id) REFERENCES dokter(id) ON DELETE SET NULL,
 FOREIGN KEY(poliklinik_id) REFERENCES poliklinik(id)
);
-- Akun demo dibuat lewat endpoint seed pertama kali (lihat README lanjutan di jawaban).

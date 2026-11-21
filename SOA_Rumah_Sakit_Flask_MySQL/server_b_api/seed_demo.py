from werkzeug.security import generate_password_hash
from config import Config
import mysql.connector

db=mysql.connector.connect(host=Config.MYSQL_HOST,port=Config.MYSQL_PORT,user=Config.MYSQL_USER,password=Config.MYSQL_PASSWORD,database=Config.MYSQL_DATABASE)
cur=db.cursor()
accounts=[
 ('admin','admin123','Administrator','admin','admin@rumahsakit.local'),
 ('dokter','dokter123','Dokter Demo','dokter','dokter@rumahsakit.local'),
 ('petugas','petugas123','Petugas Demo','petugas','petugas@rumahsakit.local'),
 ('pasien','pasien123','Pasien Demo','pasien','pasien@rumahsakit.local')]
for username,password,nama,role,email in accounts:
 cur.execute('SELECT id FROM pengguna WHERE username=%s',(username,))
 if not cur.fetchone():
  cur.execute('INSERT INTO pengguna(username,password_hash,nama_lengkap,role,email) VALUES(%s,%s,%s,%s,%s)',
   (username,generate_password_hash(password),nama,role,email))
cur.execute("SELECT id FROM poliklinik WHERE nama_poliklinik='Poli Umum'")
poli=cur.fetchone()
if not poli:
 cur.execute("INSERT INTO poliklinik(nama_poliklinik,lokasi,keterangan) VALUES('Poli Umum','Lantai 1','Pelayanan umum')")
 poli_id=cur.lastrowid
else: poli_id=poli[0]
cur.execute("SELECT id FROM pengguna WHERE username='dokter'")
dokter_user=cur.fetchone()[0]
cur.execute("SELECT id FROM dokter WHERE pengguna_id=%s",(dokter_user,))
if not cur.fetchone():
 cur.execute("INSERT INTO dokter(pengguna_id,poliklinik_id,no_sip,spesialisasi) VALUES(%s,%s,'SIP-DEMO-001','Dokter Umum')",(dokter_user,poli_id))
cur.execute("SELECT id FROM pengguna WHERE username='pasien'")
pasien_user=cur.fetchone()[0]
cur.execute("SELECT id FROM pasien WHERE pengguna_id=%s",(pasien_user,))
if not cur.fetchone():
 cur.execute("INSERT INTO pasien(pengguna_id,no_rm,jenis_kelamin,alamat) VALUES(%s,'RM-0001','L','Alamat pasien demo')",(pasien_user,))
db.commit(); cur.close(); db.close()
print('Akun demo dan data awal berhasil disiapkan.')

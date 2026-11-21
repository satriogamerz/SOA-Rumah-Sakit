from flask import Flask,request,jsonify,g
from werkzeug.security import check_password_hash,generate_password_hash
from itsdangerous import URLSafeTimedSerializer,BadSignature,SignatureExpired
from functools import wraps
from config import Config
from db import run,conn
app=Flask(__name__); app.config.from_object(Config)
ser=URLSafeTimedSerializer(app.config["SECRET_KEY"])
RES={
'poliklinik':('poliklinik',['nama_poliklinik','lokasi','keterangan'],['admin','petugas','dokter']),
'pengguna':('pengguna',['username','nama_lengkap','role','email','aktif'],['admin']),
'dokter':('dokter',['pengguna_id','poliklinik_id','no_sip','spesialisasi','no_telepon'],['admin','petugas']),
'pasien':('pasien',['pengguna_id','no_rm','tanggal_lahir','jenis_kelamin','alamat','no_telepon','asuransi_id','no_peserta'],['admin','petugas','dokter']),
'asuransi':('asuransi',['nama_asuransi','jenis','nomor_kontak','keterangan'],['admin','petugas']),
'pendaftaran':('pendaftaran',['pasien_id','dokter_id','poliklinik_id','tanggal_kunjungan','keluhan','status'],['admin','petugas','dokter'])}
def auth(fn):
 @wraps(fn)
 def w(*a,**k):
  h=request.headers.get('Authorization','')
  if not h.startswith('Bearer '): return jsonify(error='Token diperlukan'),401
  try: g.user=ser.loads(h[7:],max_age=28800)
  except (BadSignature,SignatureExpired): return jsonify(error='Token tidak valid/kedaluwarsa'),401
  return fn(*a,**k)
 return w
def allowed(resource):
 cfg=RES.get(resource)
 if not cfg: return None
 if g.user['role'] not in cfg[2]: return False
 return cfg
@app.get('/api/health')
def health(): return jsonify(status='ok',service='Rumah Sakit REST API')
@app.post('/api/login')
def login():
 d=request.get_json(silent=True) or {}
 u=run('SELECT id,username,password_hash,nama_lengkap,role,email FROM pengguna WHERE username=%s AND aktif=1',(d.get('username',''),))
 if not u or not check_password_hash(u['password_hash'],d.get('password','')): return jsonify(error='Username atau password salah'),401
 u.pop('password_hash'); return jsonify(token=ser.dumps(u),user=u)
@app.get('/api/me')
@auth
def me(): return jsonify(user=g.user)
@app.route('/api/<resource>',methods=['GET','POST'])
@auth
def collection(resource):
 c=allowed(resource)
 if c is None: return jsonify(error='Resource tidak ditemukan'),404
 if c is False: return jsonify(error='Akses ditolak'),403
 table,fields,_=c
 if request.method=='GET':
  rows=run(f'SELECT * FROM {table} ORDER BY id DESC',many=True)
  for row in rows:
   if resource=='pengguna': row.pop('password_hash',None)
   for key,val in row.items():
    if hasattr(val,'isoformat'): row[key]=val.isoformat()
  return jsonify(data=rows)
 d=request.get_json(silent=True) or {}
 if resource=='pengguna':
  if not d.get('password'): return jsonify(error='Password wajib diisi'),400
  d['password_hash']=generate_password_hash(d['password'])
  fields=fields+['password_hash']
 cols=[x for x in fields if x in d]
 if not cols: return jsonify(error='Data kosong'),400
 vals=[d[x] for x in cols]
 db=conn(); cur=db.cursor()
 cur.execute(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})",vals)
 new_id=cur.lastrowid; db.commit(); cur.close(); db.close()
 return jsonify(message='Data ditambahkan',id=new_id),201
@app.route('/api/<resource>/<int:item_id>',methods=['PUT','DELETE'])
@auth
def item(resource,item_id):
 c=allowed(resource)
 if c is None: return jsonify(error='Resource tidak ditemukan'),404
 if c is False: return jsonify(error='Akses ditolak'),403
 table,fields,_=c
 if request.method=='DELETE':
  if g.user['role']!='admin': return jsonify(error='Hanya admin yang dapat menghapus'),403
  run(f'DELETE FROM {table} WHERE id=%s',(item_id,))
  return jsonify(message='Data dihapus')
 d=request.get_json(silent=True) or {}; cols=[x for x in fields if x in d]
 if not cols: return jsonify(error='Tidak ada perubahan'),400
 run(f"UPDATE {table} SET "+','.join(f'{x}=%s' for x in cols)+' WHERE id=%s',tuple(d[x] for x in cols)+(item_id,))
 return jsonify(message='Data diperbarui')
@app.get('/api/reports/summary')
@auth
def summary():
 if g.user['role'] not in ['admin','petugas','dokter']: return jsonify(error='Akses ditolak'),403
 return jsonify(data={t:run(f'SELECT COUNT(*) total FROM {t}')['total'] for t in ['pengguna','dokter','pasien','poliklinik','asuransi','pendaftaran']})
@app.get('/api/reports/patients')
@auth
def patients_report():
 if g.user['role'] not in ['admin','petugas','dokter']: return jsonify(error='Akses ditolak'),403
 rows=run('SELECT p.id,p.no_rm,u.nama_lengkap,p.jenis_kelamin,p.no_telepon,a.nama_asuransi FROM pasien p JOIN pengguna u ON p.pengguna_id=u.id LEFT JOIN asuransi a ON p.asuransi_id=a.id ORDER BY p.id DESC',many=True)
 return jsonify(data=rows)
if __name__=='__main__': app.run(host='0.0.0.0',port=5001,debug=True)

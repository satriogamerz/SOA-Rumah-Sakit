from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from functools import wraps
import requests

app = Flask(__name__)
app.config.from_object(Config)

RESOURCES = [
    'poliklinik',
    'pengguna',
    'dokter',
    'pasien',
    'asuransi',
    'pendaftaran'
]


# ==================================================
# KOMUNIKASI DENGAN SERVER B
# ==================================================

def call(path, method='GET', payload=None):
    headers = {}

    if session.get('token'):
        headers['Authorization'] = 'Bearer ' + session['token']

    try:
        r = requests.request(
            method,
            app.config['API_BASE_URL'] + path,
            json=payload,
            headers=headers,
            timeout=8
        )

        try:
            return r.json(), r.status_code
        except ValueError:
            return {'error': 'Respons Server B tidak valid'}, r.status_code

    except requests.RequestException:
        return {'error': 'Server B tidak dapat dihubungi'}, 503


# ==================================================
# PEMERIKSAAN LOGIN DAN ROLE
# ==================================================

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('token'):
            return redirect('/login')
        return fn(*args, **kwargs)
    return wrapper


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get('token'):
                return redirect('/login')

            if session.get('user', {}).get('role') not in roles:
                flash('Anda tidak memiliki hak akses.')
                return redirect('/dashboard')

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def can_read(resource):
    role = session.get('user', {}).get('role')

    permissions = {
        'admin': RESOURCES,
        'petugas': RESOURCES,
        'dokter': [
            'poliklinik', 'dokter', 'pasien',
            'asuransi', 'pendaftaran'
        ],
        'pasien': [
            'poliklinik', 'dokter', 'pasien',
            'asuransi', 'pendaftaran'
        ]
    }

    return resource in permissions.get(role, [])


# ==================================================
# TEMPLATE USER
# ==================================================

@app.context_processor
def ctx():
    return {'user': session.get('user')}


# ==================================================
# HALAMAN UTAMA
# ==================================================

@app.get('/')
def home():
    if session.get('token'):
        return redirect('/dashboard')

    return render_template('landing.html')


# ==================================================
# LOGIN
# ==================================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        d, status = call(
            '/api/login',
            'POST',
            {
                'username': request.form.get('username'),
                'password': request.form.get('password')
            }
        )

        if status == 200:
            session.clear()
            session['token'] = d['token']
            session['user'] = d['user']

            return redirect('/dashboard')

        flash(d.get('error', 'Login gagal'))

    return render_template('login.html')


# ==================================================
# LOGOUT
# ==================================================

@app.get('/logout')
def logout():
    session.clear()
    return redirect('/')


# ==================================================
# DASHBOARD
# ==================================================

@app.get('/dashboard')
@login_required
def dashboard():

    d, status = call('/api/reports/summary')

    return render_template(
        'dashboard.html',
        summary=d.get('data', {}),
        error=d.get('error')
    )


# ==================================================
# MENAMPILKAN DATA
# ==================================================

@app.get('/data/<resource>')
@login_required
def data(resource):

    if resource not in RESOURCES:
        return 'Data tidak ditemukan', 404

    if not can_read(resource):
        flash('Anda tidak memiliki akses ke modul ini.')
        return redirect('/dashboard')

    d, status = call('/api/' + resource)

    return render_template(
        'data.html',
        resource=resource,
        rows=d.get('data', []),
        error=d.get('error')
    )


# ==================================================
# TAMBAH DATA
# ==================================================

@app.route('/tambah/<resource>', methods=['GET', 'POST'])
@login_required
def tambah(resource):

    if resource not in RESOURCES:
        return 'Data tidak ditemukan', 404

    role = session.get('user', {}).get('role')

    allowed_add = {
        'admin': RESOURCES,
        'petugas': RESOURCES,
        'dokter': [],
        'pasien': ['pendaftaran']
    }

    if resource not in allowed_add.get(role, []):
        flash('Anda tidak memiliki izin menambah data.')
        return redirect('/data/' + resource)

    # Mengambil daftar dokter dan poliklinik dari Server B
    dokter = []
    poliklinik = []

    if resource == 'pendaftaran':
        dokter_response, dokter_status = call('/api/dokter')
        poli_response, poli_status = call('/api/poliklinik')

        if dokter_status == 200:
            dokter = dokter_response.get('data', [])

        if poli_status == 200:
            poliklinik = poli_response.get('data', [])

    if request.method == 'POST':

        payload = request.form.to_dict()

        d, status = call(
            '/api/' + resource,
            'POST',
            payload
        )

        if status in [200, 201]:
            flash(d.get('message', 'Data berhasil ditambahkan'))
        else:
            flash(d.get('error', 'Gagal menambahkan data'))

        return redirect(url_for('data', resource=resource))

    return render_template(
        'add.html',
        resource=resource,
        dokter=dokter,
        poliklinik=poliklinik
    )


# ==================================================
# EDIT DATA
# ==================================================

@app.route('/edit/<resource>/<int:item_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'petugas')
def edit(resource, item_id):

    if resource not in RESOURCES:
        return 'Data tidak ditemukan', 404

    d, status = call('/api/' + resource)

    if status != 200:
        flash(d.get('error', 'Gagal mengambil data'))
        return redirect(url_for('data', resource=resource))

    row = next(
        (item for item in d.get('data', [])
         if int(item.get('id', 0)) == item_id),
        None
    )

    if not row:
        flash('Data tidak ditemukan.')
        return redirect(url_for('data', resource=resource))

    if request.method == 'POST':

        payload = request.form.to_dict()

        d, status = call(
            f'/api/{resource}/{item_id}',
            'PUT',
            payload
        )

        if status == 200:
            flash(d.get('message', 'Data berhasil diperbarui'))
        else:
            flash(d.get('error', 'Gagal memperbarui data'))

        return redirect(url_for('data', resource=resource))

    return render_template(
        'edit.html',
        resource=resource,
        row=row
    )


# ==================================================
# HAPUS DATA
# ==================================================

@app.post('/hapus/<resource>/<int:item_id>')
@login_required
@role_required('admin')
def hapus(resource, item_id):

    if resource not in RESOURCES:
        return 'Data tidak ditemukan', 404

    d, status = call(
        f'/api/{resource}/{item_id}',
        'DELETE'
    )

    if status == 200:
        flash(d.get('message', 'Data berhasil dihapus'))
    else:
        flash(d.get('error', 'Gagal menghapus data'))

    return redirect(url_for('data', resource=resource))


# ==================================================
# LAPORAN
# ==================================================

@app.get('/laporan')
@login_required
@role_required('admin', 'petugas', 'dokter')
def laporan():

    d, status = call('/api/reports/patients')

    return render_template(
        'report.html',
        rows=d.get('data', []),
        error=d.get('error')
    )


# ==================================================
# MENJALANKAN SERVER A
# ==================================================

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
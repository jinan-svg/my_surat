from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import send_file, make_response

from io import BytesIO

from openpyxl import Workbook

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import os
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, SuratMasuk, SuratKeluar


app = Flask(__name__)

from datetime import timedelta

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.permanent_session_lifetime = timedelta(minutes=30)

@app.errorhandler(413)
def too_large(e):
    flash("Ukuran file terlalu besar! Maksimal 5MB.", "danger")
    
    surat_disetujui = SuratKeluar.query.filter_by(status="Disetujui").all()

    return render_template(
        "upload_surat.html",
        surat_disetujui=surat_disetujui
    )

        
       

app.config.from_object(Config)

app.config["SECRET_KEY"] = "mysurat_secret_key"

db.init_app(app)
with app.app_context():
    db.create_all()


# =====================================
# HALAMAN AWAL
# =====================================

@app.route("/")
def index():

    # BELUM LOGIN
    if "user_id" not in session:
        return redirect(url_for("login"))

    # JIKA ADMIN
    if session.get("role") == "admin":
        return redirect(url_for("dashboard_admin"))

    # JIKA STAFF
    return redirect(url_for("dashboard"))


# =====================================
# LOGIN
# =====================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        print("USERNAME:", username)
        print("PASSWORD:", password)

        user = User.query.filter(
            (User.username == username) |
            (User.email == username)
        ).first()

        print("USER DITEMUKAN:", user)

        if user:
            print("ROLE:", user.role)

        if user and check_password_hash(user.password, password):

            print("PASSWORD BENAR")

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            if user.role == "admin":
                return redirect("/dashboard-admin")

            else:
                return redirect("/dashboard")

        print("LOGIN GAGAL")

    return render_template("login.html")

# =====================================
# REGISTER
# =====================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        nama = request.form.get("nama")
        email = request.form.get("email")
        password = request.form.get("password")
        konfirmasi = request.form.get("konfirmasi")

        if password != konfirmasi:

            flash("Konfirmasi password tidak sama!", "error")

            return redirect(url_for("register"))

        cek_user = User.query.filter(
            (User.username == nama) |
            (User.email == email)
        ).first()

        if cek_user:

            flash("Username atau email sudah terdaftar!", "error")

            return redirect(url_for("register"))

        user_baru = User(
            username=nama,
            email=email,
            password=generate_password_hash(password),
            role="Staff"
        )

        db.session.add(user_baru)
        db.session.commit()

        flash("Register berhasil!", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


# =====================================
# DASHBOARD
# =====================================


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    total_masuk = SuratMasuk.query.count()
    total_keluar = SuratKeluar.query.count()
    total_arsip = total_masuk + total_keluar

    return render_template(
        "dashboard.html",
        total_masuk=total_masuk,
        total_keluar=total_keluar,
        total_arsip=total_arsip
    )

@app.route("/dashboard-admin")
def dashboard_admin():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    total_masuk = SuratMasuk.query.count()
    total_keluar = SuratKeluar.query.count()
    total_arsip = total_masuk + total_keluar
    total_user = User.query.count()

    pending = SuratKeluar.query.filter_by(
        status="Pending"
    ).count()

    return render_template(
        "dashboard_admin.html",
        total_masuk=total_masuk,
        total_keluar=total_keluar,
        total_arsip=total_arsip,
        total_user=total_user,
        pending=pending
    )


# =====================================
# PENGAJUAN ADMIN
# =====================================

@app.route("/pengajuan-admin")
def pengajuan_admin():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # HANYA ADMIN YANG BISA MASUK
    if session.get("role") != "admin":

        flash("Akses ditolak!", "error")

        return redirect(url_for("dashboard"))

    data_surat = SuratKeluar.query.filter_by(
        status="Pending"
    ).all()

    total_pending = SuratKeluar.query.filter_by(
        status="Pending"
    ).count()

    total_disetujui = SuratKeluar.query.filter_by(
        status="Disetujui"
    ).count()

    total_ditolak = SuratKeluar.query.filter_by(
        status="Ditolak"
    ).count()

    return render_template(
        "pengajuan_admin.html",

        data_surat=data_surat,

        total_pending=total_pending,
        total_disetujui=total_disetujui,
        total_ditolak=total_ditolak
    )

@app.route("/detail-pengajuan/<int:id>")
def detail_pengajuan(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    surat = SuratKeluar.query.get_or_404(id)

    return render_template(
        "detail_pengajuan.html",
        surat=surat
    )

# =====================================
# SETUJUI SURAT
# =====================================

@app.route('/setujui-surat/<int:id>')
def setujui_surat(id):

    surat = SuratKeluar.query.get_or_404(id)

    surat.status = "Disetujui"

    db.session.commit()

    flash("Surat berhasil disetujui!", "success")

    return redirect(url_for('pengajuan_admin'))


# =====================================
# TOLAK SURAT
# =====================================

@app.route('/tolak-surat/<int:id>')
def tolak_surat(id):

    surat = SuratKeluar.query.get_or_404(id)

    surat.status = "Ditolak"

    db.session.commit()

    flash("Surat berhasil ditolak!", "error")

    return redirect(url_for('pengajuan_admin'))

@app.route("/revisi-admin/<int:id>", methods=["GET", "POST"])
def revisi_admin(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    surat = SuratKeluar.query.get_or_404(id)

    if request.method == "POST":

        catatan = request.form.get("catatan")

        surat.status = "Revisi"
        surat.catatan_revisi = catatan

        db.session.commit()

        flash("Surat dikembalikan untuk revisi!", "warning")

        return redirect(url_for("pengajuan_admin"))

    return render_template(
        "revisi_admin.html",
        surat=surat
    )


# =====================================
# LOGOUT
# =====================================

@app.route("/logout")
def logout():

    session.clear()

    response = redirect(url_for("login"))

    response.delete_cookie("session")

    return response


# =====================================
# SURAT MASUK
# =====================================

@app.route("/surat-masuk", methods=["GET", "POST"])
def surat_masuk():

    # CEK LOGIN
    if "user_id" not in session:
        return redirect(url_for("login"))

    # CEK ROLE ADMIN
    if session.get("role") != "admin":

        flash("Hanya admin yang bisa membuka halaman surat masuk!", "error")

        return redirect(url_for("dashboard"))

    # TAMBAH SURAT
    if request.method == "POST":

        nomor_surat = request.form.get("nomor_surat")
        pengirim = request.form.get("pengirim")
        perihal = request.form.get("perihal")

        file = request.files.get("file")

        filename = None

        if file and file.filename != "":

            upload_folder = app.config["UPLOAD_FOLDER"]

            os.makedirs(upload_folder, exist_ok=True)

            filename = secure_filename(file.filename)

            file.save(os.path.join(upload_folder, filename))

        surat = SuratMasuk(
            nomor_surat=nomor_surat,
            pengirim=pengirim,
            perihal=perihal,
            file_path=filename,
            created_by=session["user_id"]
        )

        db.session.add(surat)
        db.session.commit()

        flash("Surat masuk berhasil ditambahkan!", "success")

        return redirect(url_for("surat_masuk"))

    # TAMPIL DATA
    data_surat = SuratMasuk.query.order_by(
        SuratMasuk.tanggal.desc()
    ).all()

    return render_template(
        "surat_masuk.html",
        surat_list=data_surat
    )

# =====================================
# SURAT BARU
# =====================================

@app.route("/surat-baru", methods=["GET", "POST"])
def surat_baru():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        nomor_surat = request.form.get("nomor_surat")
        tujuan = request.form.get("tujuan")
        perihal = request.form.get("perihal")

        isi_tugas = request.form.get("isi_tugas")

        isi = request.form.get("isi")

        isi = isi if isi else isi_tugas

        file = request.files.get("file")

        filename = None

        if file and file.filename != "":
            filename = secure_filename(file.filename)

            file.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

        surat = SuratKeluar(
            nomor_surat=nomor_surat,
            jenis_template="surat_biasa",
            tujuan=tujuan,
            perihal=perihal,
            isi=isi if isi else "",
            file_path=filename,
            status="Pending",
            created_by=session["user_id"]
        )

        db.session.add(surat)
        db.session.commit()

        flash("Surat berhasil diajukan!", "success")

        return redirect(url_for("pengajuan"))

    return render_template("surat_baru.html")

# =====================================
# SURAT KELUAR
# =====================================

@app.route("/surat-keluar")
def surat_keluar():

    if "user_id" not in session:
        return redirect(url_for("login"))

    data_surat = SuratKeluar.query.all()

    return render_template(
        "surat_keluar.html",
        data_surat=data_surat
    )


# =====================================
# DETAIL SURAT KELUAR
# =====================================

@app.route("/detail-surat-keluar/<int:id>")
def detail_surat_keluar(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    surat = SuratKeluar.query.get_or_404(id)

    return render_template(
        "detail_surat_keluar.html",
        surat=surat
    )


# =====================================
# EDIT SURAT KELUAR
# =====================================

@app.route("/edit-surat-keluar/<int:id>", methods=["GET", "POST"])
def edit_surat_keluar(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    surat = SuratKeluar.query.get_or_404(id)

    if request.method == "POST":

        surat.nomor_surat = request.form.get("nomor_surat")
        surat.tujuan = request.form.get("tujuan")
        surat.perihal = request.form.get("perihal")
        surat.isi = request.form.get("isi")

        db.session.commit()

        flash("Surat berhasil diupdate!", "success")

        return redirect(url_for("surat_keluar"))

    return render_template(
        "edit_surat.html",
        surat=surat
    )


# =====================================
# HAPUS SURAT KELUAR
# =====================================

@app.route("/hapus-surat-keluar/<int:id>")
def hapus_surat_keluar(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    surat = SuratKeluar.query.get_or_404(id)

    db.session.delete(surat)

    db.session.commit()

    flash("Surat berhasil dihapus!", "success")

    return redirect(url_for("surat_keluar"))


# =====================================
# PENGAJUAN USER
# =====================================

@app.route("/pengajuan")
def pengajuan():

    if "user_id" not in session:
        return redirect(url_for("login"))

    data_surat = SuratKeluar.query.filter_by(
        created_by=session["user_id"]
    ).all()

    return render_template(
        "pengajuan.html",
        data_surat=data_surat
    )


# =====================================
# UPLOAD SURAT
# =====================================

@app.route("/upload-surat", methods=["GET", "POST"])
def upload_surat():

    if "user_id" not in session:
        return redirect(url_for("login"))

    surat_disetujui = SuratKeluar.query.all()

    if request.method == "POST":

        surat_id = request.form.get("surat_id")
        file = request.files.get("file_surat")

        # CEK UKURAN FILE
        if file:
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            file.seek(0)

            if file_length > 5 * 1024 * 1024:
                flash("Ukuran file terlalu besar! Maksimal 5MB.", "danger")

                return render_template(
                    "upload_surat.html",
                    surat_disetujui=surat_disetujui
                )

        # UPLOAD FILE
        if file and surat_id:

            filename = secure_filename(file.filename)

            upload_folder = os.path.join("static", "uploads")

            os.makedirs(upload_folder, exist_ok=True)

            file_path = os.path.join(upload_folder, filename)

            file.save(file_path)

            surat = SuratKeluar.query.get(surat_id)

            if surat:
                surat.file_path = filename
                db.session.commit()

            flash("File surat berhasil diupload!", "success")

            return redirect(url_for("upload_surat"))

    return render_template(
        "upload_surat.html",
        surat_disetujui=surat_disetujui
    )


# =====================================
# ARSIP
# =====================================

@app.route("/arsip")
def arsip():

    if "user_id" not in session:
        return redirect(url_for("login"))

    data_surat_masuk = SuratMasuk.query.order_by(
        SuratMasuk.tanggal.desc()
    ).all()

    data_surat_keluar = SuratKeluar.query.filter_by(
        status="Disetujui"
    ).all()

    return render_template(
        "arsip.html",
        surat_masuk=data_surat_masuk,
        surat_keluar=data_surat_keluar
    )


# =====================================
# PREVIEW FILE
# =====================================

@app.route("/preview/<filename>")
def preview_file(filename):

    if "user_id" not in session:
        return redirect(url_for("login"))

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# =====================================
# DOWNLOAD FILE
# =====================================

@app.route("/download-file/<filename>")
def download_file(filename):


    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )


# =====================================
# EXPORT PDF
# =====================================

@app.route("/download-pdf/<int:id>")
def download_pdf(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    surat = SuratKeluar.query.get_or_404(id)

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b>SURAT KELUAR</b>", styles['Title'])
    )

    elements.append(Spacer(1, 20))

    isi = f"""
    <b>Nomor Surat:</b> {surat.nomor_surat}<br/>
    <b>Tujuan:</b> {surat.tujuan}<br/>
    <b>Perihal:</b> {surat.perihal}<br/>
    <b>Status:</b> {surat.status}<br/>
    """

    elements.append(
        Paragraph(isi, styles['BodyText'])
    )

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"surat_{surat.nomor_surat}.pdf",
        mimetype='application/pdf'
    )


# =====================================
# EXPORT EXCEL
# =====================================

@app.route("/export-excel")
def export_excel():

    if "user_id" not in session:
        return redirect(url_for("login"))

    data = SuratKeluar.query.all()

    wb = Workbook()
    ws = wb.active

    ws.title = "Laporan Surat Keluar"

    ws.append([
        "No",
        "Nomor Surat",
        "Tujuan",
        "Perihal",
        "Status"
    ])

    for i, surat in enumerate(data, start=1):

        ws.append([
            i,
            surat.nomor_surat,
            surat.tujuan,
            surat.perihal,
            surat.status
        ])

    response = make_response()

    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=laporan_surat_keluar.xlsx"

    response.headers[
        "Content-type"
    ] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    wb.save("laporan_surat_keluar.xlsx")

    with open("laporan_surat_keluar.xlsx", "rb") as f:
        response.data = f.read()

    return response





# =========================
# DATABASE
# =========================

with app.app_context():
    db.create_all()


# =====================================
# RUN APP
# =====================================

@app.route("/cari-surat")
def cari_surat():

    if "user_id" not in session:
        return redirect(url_for("login"))

    keyword = request.args.get("keyword")

    hasil_masuk = []
    hasil_keluar = []

    if keyword:

        hasil_masuk = SuratMasuk.query.filter(
            (SuratMasuk.nomor_surat.like(f"%{keyword}%")) |
            (SuratMasuk.pengirim.like(f"%{keyword}%")) |
            (SuratMasuk.perihal.like(f"%{keyword}%"))
        ).all()

        hasil_keluar = SuratKeluar.query.filter(
            (SuratKeluar.nomor_surat.like(f"%{keyword}%")) |
            (SuratKeluar.tujuan.like(f"%{keyword}%")) |
            (SuratKeluar.perihal.like(f"%{keyword}%"))
        ).all()

    return render_template(
        "cari_surat.html",
        hasil_masuk=hasil_masuk,
        hasil_keluar=hasil_keluar,
        keyword=keyword
    )

if __name__ == "__main__":
    app.run(debug=True)
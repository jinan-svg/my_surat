from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="Staff"
    )


class SuratMasuk(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nomor_surat = db.Column(
        db.String(50),
        nullable=False
    )

    pengirim = db.Column(db.String(100))

    tanggal = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    perihal = db.Column(db.String(255))

    file_path = db.Column(db.String(255))

    status = db.Column(
        db.String(20),
        default="Draft"
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


class SuratKeluar(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nomor_surat = db.Column(
        db.String(50),
        nullable=False
    )

    jenis_template = db.Column(
        db.String(30),
        nullable=False
    )

    tujuan = db.Column(db.String(100))

    tanggal = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    perihal = db.Column(db.String(255))

    isi = db.Column(db.Text)

    file_path = db.Column(db.String(255))

    # STATUS SISTEM APPROVAL
    status = db.Column(
        db.String(30),
        default="Pending"
    )

    # Pending
    # Disetujui
    # Ditolak
    # Revisi

    catatan_revisi = db.Column(db.Text)

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    approved_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    approved_at = db.Column(db.DateTime)


class SuratUndangan(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    surat_keluar_id = db.Column(
        db.Integer,
        db.ForeignKey("surat_keluar.id")
    )

    nama = db.Column(db.String(100))

    alamat = db.Column(db.String(255))

    lampiran = db.Column(db.String(100))

    hari_tanggal = db.Column(db.String(100))

    waktu = db.Column(db.String(50))

    perihal = db.Column(db.String(255))


class SuratTugas(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    surat_keluar_id = db.Column(
        db.Integer,
        db.ForeignKey("surat_keluar.id")
    )

    nama = db.Column(db.String(100))

    nama_sarana = db.Column(db.String(100))

    tujuan = db.Column(db.String(255))

    tanggal = db.Column(db.String(100))

    waktu = db.Column(db.String(50))


class PersetujuanSurat(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    surat_keluar_id = db.Column(
        db.Integer,
        db.ForeignKey("surat_keluar.id")
    )

    kepala_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    status = db.Column(
        db.String(30),
        default="Menunggu"
    )

    # Menunggu
    # Disetujui
    # Ditolak
    # Revisi

    catatan = db.Column(db.Text)

    tanggal = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Disposisi(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    surat_masuk_id = db.Column(
        db.Integer,
        db.ForeignKey("surat_masuk.id")
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    catatan = db.Column(db.Text)

    tanggal = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
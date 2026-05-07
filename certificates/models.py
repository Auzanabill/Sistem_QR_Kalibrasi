import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class UserProfile(models.Model):
    """Extended user profile with login attempt tracking."""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('scanner', 'Scanner'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nama_lengkap = models.CharField('Nama Lengkap', max_length=200)
    instansi = models.CharField('Instansi/Perusahaan', max_length=200, blank=True)
    no_telp = models.CharField('No. Telepon', max_length=20, blank=True)
    role = models.CharField('Role', max_length=10, choices=ROLE_CHOICES, default='scanner')
    is_blocked = models.BooleanField('Diblokir', default=False)
    failed_attempts = models.IntegerField('Percobaan Gagal', default=0)
    blocked_at = models.DateTimeField('Waktu Diblokir', null=True, blank=True)

    class Meta:
        verbose_name = 'Profil Pengguna'
        verbose_name_plural = 'Profil Pengguna'

    def __str__(self):
        return f"{self.nama_lengkap} ({self.user.username})"

    def increment_failed_attempts(self):
        self.failed_attempts += 1
        if self.failed_attempts >= 3:
            self.is_blocked = True
            self.blocked_at = timezone.now()
        self.save()

    def reset_failed_attempts(self):
        self.failed_attempts = 0
        self.is_blocked = False
        self.blocked_at = None
        self.save()


class Instrument(models.Model):
    """Model for calibrated instruments/equipment."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_alat = models.CharField('Nama Alat', max_length=200)
    merk = models.CharField('Merk/Brand', max_length=100, blank=True)
    model_tipe = models.CharField('Model/Tipe', max_length=100, blank=True)
    nomor_aset = models.CharField('Nomor Aset', max_length=50, blank=True, null=True, unique=True)
    nomor_seri = models.CharField('Nomor Seri', max_length=100, unique=True)
    pemilik = models.CharField('Pemilik/Instansi', max_length=200, blank=True)
    lokasi = models.CharField('Lokasi', max_length=200, blank=True)
    deskripsi = models.TextField('Deskripsi', blank=True)
    qr_code = models.ImageField('QR Code', upload_to='qrcodes/', blank=True)
    created_at = models.DateTimeField('Dibuat', auto_now_add=True)
    updated_at = models.DateTimeField('Diperbarui', auto_now=True)

    class Meta:
        verbose_name = 'Alat/Instrumen'
        verbose_name_plural = 'Alat/Instrumen'
        ordering = ['nomor_aset', 'nama_alat']

    def __str__(self):
        aset = self.nomor_aset if self.nomor_aset else "-"
        return f"{aset} - {self.nama_alat}"

    def get_latest_certificate(self):
        return self.certificates.filter(is_active=True).order_by('-tanggal_kalibrasi').first()

    def get_calibration_status(self):
        cert = self.get_latest_certificate()
        if not cert:
            return 'no_cert'
        if cert.is_expired():
            return 'expired'
        if cert.is_expiring_soon():
            return 'expiring'
        return 'valid'


class Certificate(models.Model):
    """Model for calibration certificates."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE,
        related_name='certificates', verbose_name='Alat'
    )
    nomor_sertifikat = models.CharField('Nomor Sertifikat', max_length=100, unique=True)
    tanggal_kalibrasi = models.DateField('Tanggal Kalibrasi')
    tanggal_berlaku = models.DateField('Berlaku Hingga')
    laboratorium = models.CharField('Laboratorium', max_length=200)
    teknisi = models.CharField('Teknisi', max_length=200, blank=True)
    penanggung_jawab = models.CharField('Penanggung Jawab', max_length=200, blank=True)
    file_sertifikat = models.FileField(
        'File Sertifikat (PDF)', upload_to='certificates/',
        blank=True, null=True
    )
    is_active = models.BooleanField('Aktif', default=True)
    created_at = models.DateTimeField('Dibuat', auto_now_add=True)
    updated_at = models.DateTimeField('Diperbarui', auto_now=True)

    class Meta:
        verbose_name = 'Sertifikat Kalibrasi'
        verbose_name_plural = 'Sertifikat Kalibrasi'
        ordering = ['-tanggal_kalibrasi']

    def __str__(self):
        return f"{self.nomor_sertifikat} - {self.instrument.nama_alat}"

    def is_expired(self):
        return self.tanggal_berlaku < timezone.now().date()

    def is_expiring_soon(self, days=7):
        delta = self.tanggal_berlaku - timezone.now().date()
        return 0 <= delta.days <= days

    def days_until_expiry(self):
        delta = self.tanggal_berlaku - timezone.now().date()
        return delta.days

    def get_status_display_custom(self):
        if not self.is_active:
            return 'Nonaktif'
        if self.is_expired():
            return 'Expired'
        if self.is_expiring_soon():
            return 'Segera Expired'
        return 'Berlaku'

    def get_status_class(self):
        if not self.is_active:
            return 'secondary'
        if self.is_expired():
            return 'danger'
        if self.is_expiring_soon():
            return 'warning'
        return 'success'


class AccessLog(models.Model):
    """Model to log certificate access."""
    ACTION_CHOICES = [
        ('view', 'Lihat'),
        ('download', 'Download'),
        ('login_success', 'Login Berhasil'),
        ('login_failed', 'Login Gagal'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='access_logs', verbose_name='Pengguna'
    )
    certificate = models.ForeignKey(
        Certificate, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='access_logs', verbose_name='Sertifikat'
    )
    instrument = models.ForeignKey(
        Instrument, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='access_logs', verbose_name='Alat'
    )
    action = models.CharField('Aksi', max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField('IP Address', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    accessed_at = models.DateTimeField('Waktu Akses', auto_now_add=True)
    detail = models.TextField('Detail', blank=True)

    class Meta:
        verbose_name = 'Log Akses'
        verbose_name_plural = 'Log Akses'
        ordering = ['-accessed_at']

    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{user_str} - {self.action} - {self.accessed_at}"

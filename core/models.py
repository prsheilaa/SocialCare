import re
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [('admin', 'Administrator'), ('petugas', 'Petugas')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='petugas')

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser


class Platform(models.Model):
    nama = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.nama


class AkunSosmed(models.Model):
    platform = models.ForeignKey(Platform, on_delete=models.PROTECT)
    nama_akun = models.CharField(max_length=100)
    def __str__(self): return f'{self.nama_akun} ({self.platform})'


class Kategori(models.Model):
    nama = models.CharField(max_length=80, unique=True)
    def __str__(self): return self.nama


class JenisSolusi(models.Model):
    nama = models.CharField(max_length=80, unique=True)
    def __str__(self): return self.nama


POSITIF = ['bagus', 'terima kasih', 'makasih', 'mantap', 'keren', 'puas', 'hebat', 'sukses',
           'apresiasi', 'senang', 'cepat', 'ramah', 'terbantu', 'lancar']
NEGATIF = ['mati', 'padam', 'lambat', 'kecewa', 'buruk', 'komplain', 'rusak', 'bising', 'debu',
           'polusi', 'bau', 'limbah', 'protes', 'marah', 'parah', 'mengganggu', 'bahaya', 'gangguan']


def analisis_sentimen(teks):
    t = teks.lower()
    p = sum(t.count(k) for k in POSITIF)
    n = sum(t.count(k) for k in NEGATIF)
    return 'positif' if p > n else 'negatif' if n > p else 'netral'


class Komentar(models.Model):
    SENTIMEN = [('positif', 'Positif'), ('netral', 'Netral'), ('negatif', 'Negatif')]
    PRIORITAS = [('rendah', 'Rendah'), ('sedang', 'Sedang'), ('tinggi', 'Tinggi'), ('urgent', 'Urgent')]
    STATUS = [('baru', 'Baru'), ('dianalisis', 'Dianalisis'), ('menunggu', 'Menunggu persetujuan'),
              ('disetujui', 'Disetujui'), ('ditindaklanjuti', 'Ditindaklanjuti'), ('selesai', 'Selesai')]
    akun = models.ForeignKey(AkunSosmed, on_delete=models.PROTECT)
    penulis = models.CharField(max_length=100)
    isi = models.TextField()
    waktu = models.DateTimeField(default=timezone.now)
    sentimen = models.CharField(max_length=10, choices=SENTIMEN, default='netral')
    kategori = models.ForeignKey(Kategori, null=True, blank=True, on_delete=models.SET_NULL)
    prioritas = models.CharField(max_length=10, choices=PRIORITAS, default='sedang')
    status = models.CharField(max_length=20, choices=STATUS, default='baru')
    selesai_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-waktu']
        verbose_name_plural = 'Komentar'

    def save(self, *args, **kwargs):
        if not self.pk:  # komentar baru: deteksi sentimen otomatis
            self.sentimen = analisis_sentimen(self.isi)
            if self.sentimen == 'positif':  # positif -> selesai tanpa penanganan
                self.status, self.selesai_at = 'selesai', timezone.now()
        super().save(*args, **kwargs)


class RequestRespon(models.Model):
    STATUS = [('pending', 'Menunggu'), ('disetujui', 'Disetujui'), ('ditolak', 'Ditolak')]
    komentar = models.ForeignKey(Komentar, on_delete=models.CASCADE, related_name='requests')
    petugas = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    solusi = models.ForeignKey(JenisSolusi, on_delete=models.PROTECT)
    rencana = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    dibuat = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-dibuat']
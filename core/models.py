from django.contrib.auth.models import AbstractUser
from django.db import models

# Model User kustom yang mencakup field 'role' agar admin.py tidak error
class User(AbstractUser):
    # Field atau konfigurasi yang sudah ada...
    role = models.CharField(max_length=50, blank=True, null=True)

    @property
    def is_admin(self):
        # Sesuaikan 'admin' dengan nilai role yang tersimpan di database Anda
        return self.role == 'admin'
# Model untuk menampung tabel ig_comments dari database XAMPP
class IgComments(models.Model):
    post_id = models.CharField(max_length=255, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    comment_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # PENTING: Mencegah Django mengubah/menghapus tabel di XAMPP
        db_table = 'ig_comments'

# Alias model Komentar yang mengarah ke tabel ig_comments yang sama
class Komentar(models.Model):
    post_id = models.CharField(max_length=255, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    comment_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # PENTING: Mencegah Django mengubah/menghapus tabel di XAMPP
        db_table = 'ig_comments'

# Model RequestRespon yang merujuk ke tabel di database XAMPP
class RequestRespon(models.Model):
    class Meta:
        managed = False  # PENTING: Mencegah Django mengubah/menghapus tabel di XAMPP
        db_table = 'request_respon'
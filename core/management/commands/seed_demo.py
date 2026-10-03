import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import AkunSosmed, JenisSolusi, Kategori, Komentar, Platform, RequestRespon, User

TEKS = [
    "Terima kasih PLN, petugasnya ramah dan cepat",
    "Mantap, pasokan listrik lancar, sukses terus",
    "Keren, program CSR-nya bagus dan terbantu sekali",
    "Puas dengan layanannya, apresiasi untuk tim",
    "Kapan jadwal kunjungan wisata ke PLTU Paiton dibuka?",
    "Apakah ada lowongan magang di UP Paiton?",
    "Info tarif listrik bulan ini berapa ya?",
    "Lokasi kantor UP Paiton di mana?",
    "Mohon info prosedur pengajuan proposal CSR",
    "Listrik padam sejak semalam, sangat mengecewakan",
    "Debu batu bara mengganggu warga, mohon perhatikan polusi",
    "Suara bising dari area pembangkit di malam hari, parah sekali",
    "Limbah di pantai bau dan merusak mata pencaharian nelayan",
    "Jalan rusak akibat truk batu bara, komplain warga tidak ditanggapi",
    "Lambat sekali respon admin, kecewa",
    "Gangguan listrik terus berulang, bahaya untuk usaha kami",
]
NAMA = ['Budi', 'Siti', 'Agus', 'Dewi', 'Rizky', 'Putri', 'Hendra', 'Lina', 'Dimas', 'Wulan']


class Command(BaseCommand):
    help = 'Mengisi data contoh agar dashboard terlihat nyata'

    def handle(self, *args, **opts):
        if Komentar.objects.exists():
            self.stdout.write('Data sudah ada, tidak diisi ulang.')
            return
        akun = []
        for n in ['Instagram', 'Facebook', 'X (Twitter)', 'YouTube', 'TikTok']:
            p, _ = Platform.objects.get_or_create(nama=n)
            akun.append(AkunSosmed.objects.get_or_create(platform=p, nama_akun='@plnnp_paiton')[0])
        kats = [Kategori.objects.get_or_create(nama=n)[0] for n in
                ['Gangguan listrik', 'Lingkungan', 'Kebisingan', 'CSR dan masyarakat', 'Informasi umum']]
        sols = [JenisSolusi.objects.get_or_create(nama=n)[0] for n in
                ['Balasan publik', 'Kirim DM', 'Jadwalkan kunjungan']]
        petugas = User.objects.filter(role='petugas').first() or User.objects.create_user(
            'petugas1', password='petugas123', role='petugas', first_name='Petugas Satu')
        now = timezone.now()
        for _ in range(70):
            k = Komentar(akun=random.choice(akun), penulis=random.choice(NAMA), isi=random.choice(TEKS),
                         waktu=now - timedelta(days=random.randint(0, 6), hours=random.randint(0, 23),
                                               minutes=random.randint(0, 59)))
            k.save()
            if k.status == 'selesai':
                continue
            k.status = random.choice(['baru', 'baru', 'baru', 'dianalisis', 'menunggu', 'disetujui',
                                      'ditindaklanjuti', 'selesai'])
            k.prioritas = random.choice(['rendah', 'sedang', 'sedang', 'tinggi', 'urgent'])
            if k.status != 'baru':
                k.kategori = random.choice(kats)
            if k.status == 'selesai':
                k.selesai_at = k.waktu + timedelta(hours=random.randint(1, 30))
            k.save()
            if k.status in ('menunggu', 'disetujui', 'ditindaklanjuti', 'selesai'):
                RequestRespon.objects.create(
                    komentar=k, petugas=petugas, solusi=random.choice(sols), rencana='Rencana respon contoh.',
                    status='pending' if k.status == 'menunggu' else 'disetujui')
        self.stdout.write(self.style.SUCCESS('Data contoh berhasil dibuat.'))
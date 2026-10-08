from datetime import timedelta
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils import timezone
from .models import Komentar, RequestRespon


def persen(n, total):
    return round(n * 100 / total) if total else 0


def salam():
    j = timezone.localtime().hour
    return 'Selamat pagi' if j < 11 else 'Selamat siang' if j < 15 else 'Selamat sore' if j < 18 else 'Selamat malam'


def tautan(**param):
    """Bangun query string untuk chip/tombol; parameter kosong dibuang."""
    param = {k: v for k, v in param.items() if v}
    return '?' + urlencode(param) if param else '?'


def ringkasan_sentimen(qs):
    total = qs.count()
    return dict(total=total, pos=0, net=0, neg=0, pos_p=0, net_p=0, neg_p=0, gradient='conic-gradient(#E4EBF3 0 100%)')


def batang(qs, field, labels=None):
    if not field:
        return []
    rows = list(qs.values_list(field).annotate(n=Count('id')).order_by('-n'))
    mx = max([n for _, n in rows], default=0)
    return [{'label': (labels or {}).get(v, v) or 'Belum ditentukan', 'n': n, 'p': persen(n, mx)} for v, n in rows]


def tren_7_hari():
    hari, data = timezone.localdate(), []
    for i in range(6, -1, -1):
        d = hari - timedelta(days=i)
        # Menggunakan created_at sebagai acuan waktu jika tersedia
        h = Komentar.objects.filter(created_at__date=d).count() if hasattr(Komentar, 'created_at') else 0
        x = dict(label=d.strftime('%d/%m'), pos=0, net=0, neg=0, total=h, tinggi=0, pos_p=0, net_p=0, neg_p=0)
        data.append(x)
    return data


@login_required
def dashboard(request):
    return redirect('dashboard_admin' if request.user.is_admin else 'dashboard_petugas')


@login_required
def dashboard_admin(request):
    if not request.user.is_admin:
        return redirect('dashboard_petugas')
    
    K = Komentar.objects.all()
    aktif = K.all()
    total = K.count()
    selesai = 0
    pending = RequestRespon.objects.none()  # Disesuaikan jika tabel RequestRespon belum siap

    ctx = dict(
        salam=salam(), total=total, selesai=selesai, selesai_p=persen(selesai, total),
        n_aktif=aktif.count(), n_urgent=0,
        n_pending=pending.count(), sentimen=ringkasan_sentimen(K), tren=tren_7_hari(),
        b_status=[],
        b_prioritas=[],
        b_platform=[],
        b_kategori=[],
        segera=aktif[:6],
        menunggu=pending[:5])
    return render(request, 'administrator/dashboard.html', ctx)


@login_required
def dashboard_petugas(request):
    if request.user.is_admin:
        return redirect('dashboard_admin')
    
    K = Komentar.objects.all()
    aktif = K.all()
    siap = K.none()

    q = request.GET.get('q', '').strip()
    saring = aktif
    
    if q:
        saring = saring.filter(
            Q(username__icontains=q) | 
            Q(comment_text__icontains=q) | 
            Q(caption__icontains=q)
        )

    chips = [dict(key='', label='Semua', n=aktif.count(), on=True, href=tautan(q=q))]
    
    ctx = dict(
        salam=salam(), n_baru=aktif.count(),
        n_analisis=0, n_menunggu=0,
        n_siap=siap.count(), n_selesai=0, sentimen=ringkasan_sentimen(K),
        antrian=saring[:7], f='', q=q, urut='', chips=chips, sedang_filter=bool(q),
        href_urut=tautan(q=q), href_reset=tautan(),
        siap=siap[:5],
        request_saya=RequestRespon.objects.none())
    
    return render(request, 'petugas/dashboard.html', ctx)
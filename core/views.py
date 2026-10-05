from datetime import timedelta
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
from django.db.models import Case, Count, IntegerField, Q, When
from django.shortcuts import redirect, render
from django.utils import timezone
from .models import Komentar, RequestRespon

URUT = Case(When(prioritas='urgent', then=0), When(prioritas='tinggi', then=1),
            When(prioritas='sedang', then=2), default=3, output_field=IntegerField())


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
    h = {r['sentimen']: r['n'] for r in qs.values('sentimen').annotate(n=Count('id'))}
    pos, net, neg = h.get('positif', 0), h.get('netral', 0), h.get('negatif', 0)
    p1 = pos * 100 / total if total else 0
    p2 = p1 + (net * 100 / total if total else 0)
    grad = (f'conic-gradient(#1E9E5A 0 {p1:.2f}%, #8FA3B8 {p1:.2f}% {p2:.2f}%, #D9261C {p2:.2f}% 100%)'
            if total else 'conic-gradient(#E4EBF3 0 100%)')
    return dict(total=total, pos=pos, net=net, neg=neg, pos_p=persen(pos, total),
                net_p=persen(net, total), neg_p=persen(neg, total), gradient=grad)


def batang(qs, field, labels=None):
    rows = list(qs.values_list(field).annotate(n=Count('id')).order_by('-n'))
    mx = max([n for _, n in rows], default=0)
    return [{'label': (labels or {}).get(v, v) or 'Belum ditentukan', 'n': n, 'p': persen(n, mx)} for v, n in rows]


def tren_7_hari():
    hari, data = timezone.localdate(), []
    for i in range(6, -1, -1):
        d = hari - timedelta(days=i)
        h = {r['sentimen']: r['n'] for r in
             Komentar.objects.filter(waktu__date=d).values('sentimen').annotate(n=Count('id'))}
        x = dict(label=d.strftime('%d/%m'), pos=h.get('positif', 0), net=h.get('netral', 0), neg=h.get('negatif', 0))
        x['total'] = x['pos'] + x['net'] + x['neg']
        data.append(x)
    mx = max(x['total'] for x in data) or 1
    for x in data:
        x['tinggi'] = persen(x['total'], mx)
        x['pos_p'], x['net_p'], x['neg_p'] = (persen(x[k], x['total']) for k in ('pos', 'net', 'neg'))
    return data


@login_required
def dashboard(request):
    return redirect('dashboard_admin' if request.user.is_admin else 'dashboard_petugas')


@login_required
def dashboard_admin(request):
    if not request.user.is_admin:
        return redirect('dashboard_petugas')
    K = Komentar.objects.all()
    aktif = K.exclude(sentimen='positif').exclude(status='selesai')  # komentar yang butuh penanganan
    total, selesai = K.count(), K.filter(status='selesai').count()
    pending = RequestRespon.objects.filter(status='pending')
    ctx = dict(
        salam=salam(), total=total, selesai=selesai, selesai_p=persen(selesai, total),
        n_aktif=aktif.count(), n_urgent=aktif.filter(prioritas__in=['urgent', 'tinggi']).count(),
        n_pending=pending.count(), sentimen=ringkasan_sentimen(K), tren=tren_7_hari(),
        b_status=batang(K, 'status', dict(Komentar.STATUS)),
        b_prioritas=batang(aktif, 'prioritas', dict(Komentar.PRIORITAS)),
        b_platform=batang(K, 'akun__platform__nama'),
        b_kategori=batang(K.exclude(sentimen='positif'), 'kategori__nama'),
        segera=aktif.select_related('akun__platform').annotate(u=URUT).order_by('u', '-waktu')[:6],
        menunggu=pending.select_related('komentar', 'petugas', 'solusi')[:5])
    return render(request, 'administrator/dashboard.html', ctx)


@login_required
def dashboard_petugas(request):
    if request.user.is_admin:
        return redirect('dashboard_admin')
    K = Komentar.objects.all()
    aktif = K.exclude(sentimen='positif')
    siap = aktif.filter(status__in=['disetujui', 'ditindaklanjuti'])

    # antrian prioritas: filter chip (f), pencarian (q), dan urutan (urut)
    dasar = aktif.filter(status__in=['baru', 'dianalisis'])
    f = request.GET.get('f', '')
    q = request.GET.get('q', '').strip()
    urut = 'terbaru' if request.GET.get('urut') == 'terbaru' else ''
    saring = dasar
    if f == 'urgent':
        saring = saring.filter(prioritas='urgent')
    elif f == 'tinggi':
        saring = saring.filter(prioritas='tinggi')
    elif f == 'baru':
        saring = saring.filter(status='baru')
    else:
        f = ''
    if q:
        saring = saring.filter(Q(penulis__icontains=q) | Q(isi__icontains=q) |
                               Q(akun__nama_akun__icontains=q) | Q(akun__platform__nama__icontains=q))
    saring = saring.select_related('akun__platform')
    saring = saring.order_by('-waktu') if urut else saring.annotate(u=URUT).order_by('u', '-waktu')

    chips = [dict(key=k, label=lbl, n=n, on=(f == k), href=tautan(f=k, q=q, urut=urut))
             for k, lbl, n in (('', 'Semua', dasar.count()),
                               ('urgent', 'Urgent', dasar.filter(prioritas='urgent').count()),
                               ('tinggi', 'Tinggi', dasar.filter(prioritas='tinggi').count()),
                               ('baru', 'Status Baru', None))]
    ctx = dict(
        salam=salam(), n_baru=aktif.filter(status='baru').count(),
        n_analisis=aktif.filter(status='dianalisis').count(), n_menunggu=aktif.filter(status='menunggu').count(),
        n_siap=siap.count(), n_selesai=K.filter(status='selesai').count(), sentimen=ringkasan_sentimen(K),
        antrian=saring[:7], f=f, q=q, urut=urut, chips=chips, sedang_filter=bool(f or q),
        href_urut=tautan(f=f, q=q, urut='' if urut else 'terbaru'), href_reset=tautan(urut=urut),
        siap=siap.select_related('akun__platform', 'kategori')[:5],
        request_saya=RequestRespon.objects.filter(petugas=request.user).select_related('komentar', 'solusi')[:5])
    return render(request, 'petugas/dashboard.html', ctx)
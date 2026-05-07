from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.conf import settings
from django.core.mail import send_mail

from .models import UserProfile, Instrument, Certificate, AccessLog
from .forms import LoginForm, RegisterForm, InstrumentForm, CertificateForm
from .utils import generate_qr_code, get_client_ip


def login_view(request):
    """Custom login view with 3x attempt blocking."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        username = request.POST.get('username', '')

        # Check if user is blocked
        try:
            from django.contrib.auth.models import User
            user_obj = User.objects.get(username=username)
            if hasattr(user_obj, 'profile') and user_obj.profile.is_blocked:
                messages.error(request, '❌ Akun Anda telah diblokir karena terlalu banyak percobaan login yang gagal. Hubungi administrator.')
                AccessLog.objects.create(
                    user=user_obj,
                    action='login_failed',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    detail='Akun diblokir - login ditolak',
                )
                return render(request, 'certificates/login.html', {'form': form})
        except Exception:
            pass

        if form.is_valid():
            user = form.get_user()
            # Reset failed attempts on success
            if hasattr(user, 'profile'):
                user.profile.reset_failed_attempts()

            login(request, user)

            AccessLog.objects.create(
                user=user,
                action='login_success',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )

            # Redirect to next URL or dashboard
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            # Increment failed attempts
            try:
                user_obj = User.objects.get(username=username)
                if hasattr(user_obj, 'profile'):
                    user_obj.profile.increment_failed_attempts()
                    remaining = 3 - user_obj.profile.failed_attempts
                    if user_obj.profile.is_blocked:
                        messages.error(request, '❌ Akun Anda telah diblokir karena 3x percobaan gagal. Hubungi administrator.')
                    elif remaining > 0:
                        messages.error(request, f'⚠️ Username atau password salah. Sisa percobaan: {remaining}')
                    AccessLog.objects.create(
                        user=user_obj,
                        action='login_failed',
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        detail=f'Percobaan ke-{user_obj.profile.failed_attempts}',
                    )
                else:
                    messages.error(request, '⚠️ Username atau password salah.')
            except Exception:
                messages.error(request, '⚠️ Username atau password salah.')
    else:
        form = LoginForm()

    return render(request, 'certificates/login.html', {'form': form})


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '✅ Registrasi berhasil! Selamat datang.')
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'certificates/register.html', {'form': form})


def logout_view(request):
    """Logout view."""
    logout(request)
    messages.info(request, 'Anda telah keluar dari sistem.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Main dashboard with overview statistics."""
    total_instruments = Instrument.objects.count()
    total_certificates = Certificate.objects.filter(is_active=True).count()

    # Count expired and expiring soon
    today = timezone.now().date()
    expired = Certificate.objects.filter(is_active=True, tanggal_berlaku__lt=today).count()
    expiring_soon = Certificate.objects.filter(
        is_active=True,
        tanggal_berlaku__gte=today,
        tanggal_berlaku__lte=today + timezone.timedelta(days=7)
    ).count()
    valid = total_certificates - expired - expiring_soon

    # Recent access logs
    recent_logs = AccessLog.objects.select_related('user', 'certificate', 'instrument')[:10]

    # Expiring certificates
    expiring_certs = Certificate.objects.filter(
        is_active=True,
        tanggal_berlaku__gte=today,
        tanggal_berlaku__lte=today + timezone.timedelta(days=30)
    ).select_related('instrument').order_by('tanggal_berlaku')[:5]

    context = {
        'total_instruments': total_instruments,
        'total_certificates': total_certificates,
        'expired': expired,
        'expiring_soon': expiring_soon,
        'valid': valid,
        'recent_logs': recent_logs,
        'expiring_certs': expiring_certs,
    }
    return render(request, 'certificates/dashboard.html', context)


@login_required
def instrument_list_view(request):
    """List all instruments."""
    query = request.GET.get('q', '')
    instruments = Instrument.objects.all().order_by('nomor_aset')
    if query:
        instruments = instruments.filter(
            Q(nama_alat__icontains=query) |
            Q(nomor_seri__icontains=query) |
            Q(merk__icontains=query) |
            Q(lokasi__icontains=query)
        )
    return render(request, 'certificates/instrument_list.html', {
        'instruments': instruments,
        'query': query,
    })


@login_required
def instrument_create_view(request):
    """Create a new instrument."""
    if request.method == 'POST':
        form = InstrumentForm(request.POST)
        if form.is_valid():
            instrument = form.save()
            # Auto-generate QR code
            generate_qr_code(instrument)
            messages.success(request, f'✅ Alat "{instrument.nama_alat}" berhasil ditambahkan.')
            return redirect('instrument_detail', instrument_id=instrument.id)
    else:
        form = InstrumentForm()

    return render(request, 'certificates/instrument_form.html', {
        'form': form,
        'title': 'Tambah Alat Baru',
    })


@login_required
def instrument_detail_view(request, instrument_id):
    """View instrument details with its certificates."""
    instrument = get_object_or_404(Instrument, id=instrument_id)
    certificates = instrument.certificates.all()
    return render(request, 'certificates/instrument_detail.html', {
        'instrument': instrument,
        'certificates': certificates,
    })


@login_required
def instrument_edit_view(request, instrument_id):
    """Edit an instrument."""
    instrument = get_object_or_404(Instrument, id=instrument_id)
    if request.method == 'POST':
        form = InstrumentForm(request.POST, instance=instrument)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Data alat berhasil diperbarui.')
            return redirect('instrument_detail', instrument_id=instrument.id)
    else:
        form = InstrumentForm(instance=instrument)

    return render(request, 'certificates/instrument_form.html', {
        'form': form,
        'title': f'Edit: {instrument.nama_alat}',
        'instrument': instrument,
    })


@login_required
def instrument_delete_view(request, instrument_id):
    """Delete an instrument."""
    instrument = get_object_or_404(Instrument, id=instrument_id)
    if request.method == 'POST':
        name = instrument.nama_alat
        instrument.delete()
        messages.success(request, f'✅ Alat "{name}" berhasil dihapus.')
        return redirect('instrument_list')
    return render(request, 'certificates/instrument_confirm_delete.html', {
        'instrument': instrument,
    })


@login_required
def regenerate_qr_view(request, instrument_id):
    """Regenerate QR code for an instrument."""
    instrument = get_object_or_404(Instrument, id=instrument_id)
    generate_qr_code(instrument)
    messages.success(request, f'✅ QR Code untuk "{instrument.nama_alat}" berhasil di-generate ulang.')
    return redirect('instrument_detail', instrument_id=instrument.id)


@login_required
def certificate_list_view(request):
    """List all certificates."""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    certificates = Certificate.objects.select_related('instrument').all().order_by('instrument__nomor_aset')

    if query:
        certificates = certificates.filter(
            Q(nomor_sertifikat__icontains=query) |
            Q(instrument__nama_alat__icontains=query) |
            Q(laboratorium__icontains=query)
        )

    today = timezone.now().date()
    if status == 'valid':
        certificates = certificates.filter(is_active=True, tanggal_berlaku__gte=today)
    elif status == 'expired':
        certificates = certificates.filter(is_active=True, tanggal_berlaku__lt=today)
    elif status == 'inactive':
        certificates = certificates.filter(is_active=False)

    return render(request, 'certificates/certificate_list.html', {
        'certificates': certificates,
        'query': query,
        'status': status,
    })


@login_required
def certificate_create_view(request):
    """Create a new certificate."""
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save()
            messages.success(request, f'✅ Sertifikat "{cert.nomor_sertifikat}" berhasil ditambahkan.')
            return redirect('certificate_detail', certificate_id=cert.id)
    else:
        form = CertificateForm()
        # Pre-select instrument if passed in URL
        instrument_id = request.GET.get('instrument')
        if instrument_id:
            form.fields['instrument'].initial = instrument_id

    return render(request, 'certificates/certificate_form.html', {
        'form': form,
        'title': 'Tambah Sertifikat Baru',
    })


@login_required
def certificate_detail_view(request, certificate_id):
    """View certificate details."""
    certificate = get_object_or_404(Certificate.objects.select_related('instrument'), id=certificate_id)

    # Log access
    AccessLog.objects.create(
        user=request.user,
        certificate=certificate,
        instrument=certificate.instrument,
        action='view',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )

    return render(request, 'certificates/certificate_detail.html', {
        'certificate': certificate,
    })


@login_required
def certificate_edit_view(request, certificate_id):
    """Edit a certificate."""
    certificate = get_object_or_404(Certificate, id=certificate_id)
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES, instance=certificate)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Sertifikat berhasil diperbarui.')
            return redirect('certificate_detail', certificate_id=certificate.id)
    else:
        form = CertificateForm(instance=certificate)

    return render(request, 'certificates/certificate_form.html', {
        'form': form,
        'title': f'Edit: {certificate.nomor_sertifikat}',
        'certificate': certificate,
    })


@login_required
def certificate_delete_view(request, certificate_id):
    """Delete a certificate."""
    certificate = get_object_or_404(Certificate, id=certificate_id)
    if request.method == 'POST':
        nomor = certificate.nomor_sertifikat
        certificate.delete()
        messages.success(request, f'✅ Sertifikat "{nomor}" berhasil dihapus.')
        return redirect('certificate_list')
    return render(request, 'certificates/certificate_confirm_delete.html', {
        'certificate': certificate,
    })


def scan_instrument_view(request, instrument_id):
    """Public view when QR code is scanned - redirects to login if needed."""
    instrument = get_object_or_404(Instrument, id=instrument_id)

    if not request.user.is_authenticated:
        # Store instrument ID in session for post-login redirect
        request.session['scan_instrument_id'] = str(instrument_id)
        return redirect(f'/login/?next=/scan/{instrument_id}/')

    # User is authenticated - show the latest certificate
    certificate = instrument.get_latest_certificate()

    # Log the scan access
    AccessLog.objects.create(
        user=request.user,
        instrument=instrument,
        certificate=certificate,
        action='view',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        detail=f'QR Scan - {instrument.nama_alat}',
    )

    return render(request, 'certificates/scan_result.html', {
        'instrument': instrument,
        'certificate': certificate,
    })


@login_required
def download_certificate_view(request, certificate_id):
    """Download certificate PDF file."""
    certificate = get_object_or_404(Certificate, id=certificate_id)

    if not certificate.file_sertifikat:
        messages.error(request, '❌ File sertifikat tidak tersedia.')
        return redirect('certificate_detail', certificate_id=certificate.id)

    # Log download
    AccessLog.objects.create(
        user=request.user,
        certificate=certificate,
        instrument=certificate.instrument,
        action='download',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )

    # Serve file
    response = HttpResponse(certificate.file_sertifikat.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{certificate.nomor_sertifikat}.pdf"'
    return response


@login_required
def qr_print_view(request, instrument_id):
    """Print-friendly QR code page."""
    instrument = get_object_or_404(Instrument, id=instrument_id)
    return render(request, 'certificates/qr_print.html', {
        'instrument': instrument,
    })


@login_required
def access_log_view(request):
    """View access logs (monitoring)."""
    logs = AccessLog.objects.select_related('user', 'certificate', 'instrument').all()

    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action=action_filter)

    query = request.GET.get('q', '')
    if query:
        logs = logs.filter(
            Q(user__username__icontains=query) |
            Q(instrument__nama_alat__icontains=query) |
            Q(certificate__nomor_sertifikat__icontains=query)
        )

    return render(request, 'certificates/access_log.html', {
        'logs': logs[:100],
        'action_filter': action_filter,
        'query': query,
    })


@login_required
def user_management_view(request):
    """Manage scanner users (admin only)."""
    profiles = UserProfile.objects.select_related('user').all()
    return render(request, 'certificates/user_management.html', {
        'profiles': profiles,
    })


@login_required
def unblock_user_view(request, user_id):
    """Unblock a blocked user."""
    profile = get_object_or_404(UserProfile, user_id=user_id)
    profile.reset_failed_attempts()
    messages.success(request, f'✅ User "{profile.nama_lengkap}" berhasil di-unblock.')
    return redirect('user_management')


@login_required
def send_expiry_notifications_view(request):
    """Manually trigger expiry notification emails."""
    today = timezone.now().date()
    expiring = Certificate.objects.filter(
        is_active=True,
        tanggal_berlaku__gte=today,
        tanggal_berlaku__lte=today + timezone.timedelta(days=7)
    ).select_related('instrument')

    count = 0
    for cert in expiring:
        try:
            send_mail(
                subject=f'⚠️ Sertifikat Kalibrasi Segera Expired - {cert.instrument.nama_alat}',
                message=(
                    f'Sertifikat kalibrasi berikut akan segera expired:\n\n'
                    f'Alat: {cert.instrument.nama_alat}\n'
                    f'No. Sertifikat: {cert.nomor_sertifikat}\n'
                    f'Berlaku hingga: {cert.tanggal_berlaku}\n'
                    f'Sisa hari: {cert.days_until_expiry()} hari\n\n'
                    f'Segera lakukan kalibrasi ulang.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@calibration.local',
                recipient_list=['admin@calibration.local'],
                fail_silently=True,
            )
            count += 1
        except Exception:
            pass

    messages.info(request, f'📧 {count} notifikasi email terkirim untuk sertifikat yang akan expired.')
    return redirect('dashboard')

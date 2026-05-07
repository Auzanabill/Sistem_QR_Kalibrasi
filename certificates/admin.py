from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Instrument, Certificate, AccessLog
from .utils import generate_qr_code


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['nama_lengkap', 'user', 'instansi', 'role', 'is_blocked', 'failed_attempts']
    list_filter = ['role', 'is_blocked']
    search_fields = ['nama_lengkap', 'user__username', 'instansi']
    actions = ['unblock_users']

    @admin.action(description='Unblock selected users')
    def unblock_users(self, request, queryset):
        for profile in queryset:
            profile.reset_failed_attempts()
        self.message_user(request, f'{queryset.count()} user(s) berhasil di-unblock.')


class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 0
    fields = ['nomor_sertifikat', 'tanggal_kalibrasi', 'tanggal_berlaku', 'laboratorium', 'is_active']
    readonly_fields = []


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ['nama_alat', 'merk', 'model_tipe', 'nomor_seri', 'lokasi', 'qr_code_preview']
    list_filter = ['merk', 'lokasi']
    search_fields = ['nama_alat', 'nomor_seri', 'merk']
    inlines = [CertificateInline]
    actions = ['generate_qr_codes']

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="60" height="60" />', obj.qr_code.url)
        return '-'
    qr_code_preview.short_description = 'QR Code'

    @admin.action(description='Generate QR Codes')
    def generate_qr_codes(self, request, queryset):
        for instrument in queryset:
            generate_qr_code(instrument)
        self.message_user(request, f'QR Code generated for {queryset.count()} instrument(s).')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['nomor_sertifikat', 'instrument', 'tanggal_kalibrasi', 'tanggal_berlaku', 'laboratorium', 'status_badge', 'is_active']
    list_filter = ['is_active', 'laboratorium', 'tanggal_berlaku']
    search_fields = ['nomor_sertifikat', 'instrument__nama_alat', 'laboratorium']
    date_hierarchy = 'tanggal_kalibrasi'

    def status_badge(self, obj):
        status = obj.get_status_display_custom()
        color_map = {
            'Berlaku': '#00c853',
            'Segera Expired': '#ff9100',
            'Expired': '#ff1744',
            'Nonaktif': '#9e9e9e',
        }
        color = color_map.get(status, '#9e9e9e')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 10px; border-radius:12px; font-size:11px;">{}</span>',
            color, status
        )
    status_badge.short_description = 'Status'


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['accessed_at', 'user', 'action', 'instrument', 'certificate', 'ip_address']
    list_filter = ['action', 'accessed_at']
    search_fields = ['user__username', 'instrument__nama_alat', 'ip_address']
    date_hierarchy = 'accessed_at'
    readonly_fields = ['user', 'certificate', 'instrument', 'action', 'ip_address', 'user_agent', 'accessed_at', 'detail']


# Customize admin site
admin.site.site_header = '🔬 Sistem Kalibrasi - Admin'
admin.site.site_title = 'Calibration System Admin'
admin.site.index_title = 'Dashboard Administrasi'

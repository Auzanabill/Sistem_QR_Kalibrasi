from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard_view, name='dashboard'),

    # Instruments
    path('instruments/', views.instrument_list_view, name='instrument_list'),
    path('instruments/create/', views.instrument_create_view, name='instrument_create'),
    path('instruments/<uuid:instrument_id>/', views.instrument_detail_view, name='instrument_detail'),
    path('instruments/<uuid:instrument_id>/edit/', views.instrument_edit_view, name='instrument_edit'),
    path('instruments/<uuid:instrument_id>/delete/', views.instrument_delete_view, name='instrument_delete'),
    path('instruments/<uuid:instrument_id>/regenerate-qr/', views.regenerate_qr_view, name='regenerate_qr'),
    path('instruments/<uuid:instrument_id>/print-qr/', views.qr_print_view, name='qr_print'),

    # Certificates
    path('certificates/', views.certificate_list_view, name='certificate_list'),
    path('certificates/create/', views.certificate_create_view, name='certificate_create'),
    path('certificates/<uuid:certificate_id>/', views.certificate_detail_view, name='certificate_detail'),
    path('certificates/<uuid:certificate_id>/edit/', views.certificate_edit_view, name='certificate_edit'),
    path('certificates/<uuid:certificate_id>/delete/', views.certificate_delete_view, name='certificate_delete'),
    path('certificates/<uuid:certificate_id>/download/', views.download_certificate_view, name='certificate_download'),

    # QR Scan (public)
    path('scan/<uuid:instrument_id>/', views.scan_instrument_view, name='scan_instrument'),

    # Monitoring & Admin
    path('monitoring/', views.access_log_view, name='access_log'),
    path('users/', views.user_management_view, name='user_management'),
    path('users/<int:user_id>/unblock/', views.unblock_user_view, name='unblock_user'),
    path('notifications/send/', views.send_expiry_notifications_view, name='send_notifications'),
]

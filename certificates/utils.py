import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse


def generate_qr_code(instrument):
    """Generate QR code for an instrument and save it to the instrument's qr_code field."""
    # Build the URL that the QR code will point to
    url_path = reverse('scan_instrument', kwargs={'instrument_id': str(instrument.id)})
    # For QR code, we use a relative URL - the full URL will depend on deployment
    qr_url = f"{{BASE_URL}}{url_path}"

    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url_path)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color='#1a1a2e', back_color='white')

    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Save to instrument
    filename = f"qr_{instrument.id}.png"
    instrument.qr_code.save(filename, ContentFile(buffer.read()), save=True)

    return instrument.qr_code


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

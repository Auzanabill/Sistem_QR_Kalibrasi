from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from certificates.models import Instrument, Certificate
from certificates.utils import generate_qr_code


class Command(BaseCommand):
    help = 'Seed database with sample instruments and certificates'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding sample data...')

        instruments_data = [
            {
                'nama_alat': 'Multimeter Digital',
                'merk': 'Fluke',
                'model_tipe': '87V',
                'nomor_seri': 'FLK-87V-001',
                'pemilik': 'PT. Perusahaan Internal',
                'lokasi': 'Lab Kalibrasi Lt.2',
                'deskripsi': 'Multimeter digital presisi tinggi untuk pengukuran tegangan, arus, dan resistansi',
            },
            {
                'nama_alat': 'Spectrum Analyzer',
                'merk': 'Keysight',
                'model_tipe': 'N9020B',
                'nomor_seri': 'KST-N9020B-001',
                'pemilik': 'PT. Perusahaan Internal',
                'lokasi': 'Lab RF Lt.3',
                'deskripsi': 'Spectrum analyzer untuk pengukuran sinyal RF dan microwave',
            },
            {
                'nama_alat': 'Oscilloscope',
                'merk': 'Tektronix',
                'model_tipe': 'MSO46',
                'nomor_seri': 'TEK-MSO46-001',
                'pemilik': 'PT. Perusahaan Internal',
                'lokasi': 'Lab Elektronika Lt.2',
                'deskripsi': 'Mixed signal oscilloscope 4 channel',
            },
            {
                'nama_alat': 'Signal Generator',
                'merk': 'Rohde & Schwarz',
                'model_tipe': 'SMB100A',
                'nomor_seri': 'RS-SMB100A-001',
                'pemilik': 'PT. Perusahaan Internal',
                'lokasi': 'Lab RF Lt.3',
                'deskripsi': 'Signal generator untuk pengujian perangkat telekomunikasi',
            },
            {
                'nama_alat': 'Network Analyzer',
                'merk': 'Keysight',
                'model_tipe': 'E5071C',
                'nomor_seri': 'KST-E5071C-001',
                'pemilik': 'PT. Perusahaan Internal',
                'lokasi': 'Lab Kalibrasi Lt.2',
                'deskripsi': 'Vector network analyzer untuk pengukuran parameter jaringan',
            },
        ]

        today = timezone.now().date()

        for data in instruments_data:
            instrument, created = Instrument.objects.get_or_create(
                nomor_seri=data['nomor_seri'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  Created instrument: {instrument.nama_alat}')
                generate_qr_code(instrument)
                self.stdout.write(f'  Generated QR code for: {instrument.nama_alat}')
            else:
                self.stdout.write(f'  Instrument already exists: {instrument.nama_alat}')

        # Create certificates
        instruments = Instrument.objects.all()

        cert_data = [
            # Valid certificate
            {
                'instrument': instruments[0],
                'nomor_sertifikat': 'CAL-2026-0001',
                'tanggal_kalibrasi': today - timedelta(days=60),
                'tanggal_berlaku': today + timedelta(days=305),
                'laboratorium': 'Lab Kalibrasi Internal',
                'teknisi': 'Budi Santoso',
                'penanggung_jawab': 'Dr. Ahmad Hidayat',
            },
            # Expiring soon
            {
                'instrument': instruments[1],
                'nomor_sertifikat': 'CAL-2026-0002',
                'tanggal_kalibrasi': today - timedelta(days=358),
                'tanggal_berlaku': today + timedelta(days=5),
                'laboratorium': 'Lab Kalibrasi Internal',
                'teknisi': 'Siti Rahayu',
                'penanggung_jawab': 'Dr. Ahmad Hidayat',
            },
            # Expired
            {
                'instrument': instruments[2],
                'nomor_sertifikat': 'CAL-2025-0015',
                'tanggal_kalibrasi': today - timedelta(days=400),
                'tanggal_berlaku': today - timedelta(days=35),
                'laboratorium': 'Lab Kalibrasi Internal',
                'teknisi': 'Agus Pratama',
                'penanggung_jawab': 'Dr. Ahmad Hidayat',
            },
            # Valid
            {
                'instrument': instruments[3],
                'nomor_sertifikat': 'CAL-2026-0003',
                'tanggal_kalibrasi': today - timedelta(days=30),
                'tanggal_berlaku': today + timedelta(days=335),
                'laboratorium': 'Lab Kalibrasi Internal',
                'teknisi': 'Dewi Lestari',
                'penanggung_jawab': 'Dr. Ahmad Hidayat',
            },
            # Valid
            {
                'instrument': instruments[4],
                'nomor_sertifikat': 'CAL-2026-0004',
                'tanggal_kalibrasi': today - timedelta(days=90),
                'tanggal_berlaku': today + timedelta(days=275),
                'laboratorium': 'Lab Kalibrasi Internal',
                'teknisi': 'Rizky Firmansyah',
                'penanggung_jawab': 'Dr. Ahmad Hidayat',
            },
        ]

        for data in cert_data:
            cert, created = Certificate.objects.get_or_create(
                nomor_sertifikat=data['nomor_sertifikat'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  Created certificate: {cert.nomor_sertifikat}')
            else:
                self.stdout.write(f'  Certificate already exists: {cert.nomor_sertifikat}')

        self.stdout.write(self.style.SUCCESS('\nSample data seeded successfully!'))

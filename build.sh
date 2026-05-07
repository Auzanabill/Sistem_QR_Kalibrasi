#!/usr/bin/env bash
# Script build untuk Render.com
# Dijalankan otomatis setiap kali ada deploy baru

set -o errexit  # Hentikan script jika ada error

# Install semua dependencies
pip install -r requirements.txt

# Kumpulkan static files ke folder staticfiles/
python manage.py collectstatic --no-input

# Jalankan database migrations
python manage.py migrate

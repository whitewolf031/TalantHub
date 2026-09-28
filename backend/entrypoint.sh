#!/bin/sh
set -e

echo "==> Ma'lumotlar bazasi tayyor bo'lishini kutyapmiz..."
python - <<'PYCODE'
import os
import sys
import time

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connections
from django.db.utils import OperationalError

max_attempts = 30
for attempt in range(1, max_attempts + 1):
    try:
        connections["default"].cursor()
        print("==> Baza ulanishi tayyor.")
        break
    except OperationalError:
        print(f"==> Baza hali tayyor emas ({attempt}/{max_attempts}), 2 soniyadan keyin qayta urinamiz...")
        time.sleep(2)
else:
    print("==> Bazaga ulanib bo'lmadi, dastur to'xtatildi.")
    sys.exit(1)
PYCODE

echo "==> Migratsiyalar yaratilyapti (makemigrations)..."
python manage.py makemigrations --noinput

echo "==> Migratsiyalar bazaga qo'llanyapti (migrate)..."
python manage.py migrate --noinput

echo "==> E'lon turlari (categories) fixture yuklanyapti..."
python manage.py loaddata apps/categories/fixtures/categories.json || \
    echo "==> Fixture allaqachon yuklangan yoki xatolik yuz berdi, davom etamiz."

echo "==> Superuser tekshirilyapti / yaratilyapti..."
python - <<'PYCODE'
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if not username or not password:
    print("==> DJANGO_SUPERUSER_USERNAME yoki DJANGO_SUPERUSER_PASSWORD "
          ".env'da topilmadi — superuser yaratish o'tkazib yuborildi.")
elif User.objects.filter(username=username).exists():
    print(f"==> Superuser '{username}' allaqachon mavjud, qayta yaratilmadi.")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"==> Superuser '{username}' muvaffaqiyatli yaratildi.")
PYCODE

echo "==> Statik fayllar yig'ilyapti (collectstatic)..."
python manage.py collectstatic --noinput || echo "==> collectstatic o'tkazib yuborildi."

echo "==> Server ishga tushyapti..."
exec "$@"

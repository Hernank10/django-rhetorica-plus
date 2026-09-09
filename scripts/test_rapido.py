#!/usr/bin/env python
"""Script rápido de prueba para Django"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.contrib.auth.models import User
from core.models import Ejercicio, Tecnica, Contenido
from django.db import connection
from django.test import Client

print("=== PRUEBA RÁPIDA ===\n")

# 1. Base de datos
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Conexión a BD: OK")
except Exception as e:
    print(f"❌ Error BD: {str(e)[:50]}")

# 2. Modelos
try:
    print(f"✅ Usuarios: {User.objects.count()}")
    print(f"✅ Ejercicios: {Ejercicio.objects.count()}")
    print(f"✅ Técnicas: {Tecnica.objects.count()}")
    print(f"✅ Contenidos: {Contenido.objects.count()}")
except Exception as e:
    print(f"❌ Error en modelos: {str(e)[:50]}")

# 3. URLs
try:
    client = Client()
    urls = ['/', '/login/', '/registro/', '/dashboard/']
    for url in urls:
        resp = client.get(url)
        status = "✅" if resp.status_code != 404 else "⚠️"
        print(f"{status} {url} -> {resp.status_code}")
except Exception as e:
    print(f"❌ Error en URLs: {str(e)[:50]}")

print("\n=== FIN PRUEBA ===")

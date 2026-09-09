#!/usr/bin/env python
"""Diagnosticar problemas de la API"""

import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.urls import get_resolver
from django.contrib.auth.models import User

print("=== DIAGNÓSTICO DE API ===\n")

# 1. Verificar URLs
print("📋 URLs disponibles:")
resolver = get_resolver()
for url in resolver.url_patterns:
    if 'api' in str(url.pattern):
        print(f"  {url.pattern}")

# 2. Verificar usuarios
print(f"\n👤 Usuarios: {User.objects.count()}")
if User.objects.count() > 0:
    user = User.objects.first()
    print(f"  Usuario: {user.username}")

# 3. Verificar ejercicios
from core.models import EjercicioLinguistico
print(f"\n📊 Ejercicios: {EjercicioLinguistico.objects.count()}")

# 4. Probar la vista
try:
    from core.views_api import ejercicios_json
    print("\n✅ Vista de API encontrada")
except Exception as e:
    print(f"\n❌ Error en vista de API: {e}")

print("\n✅ Diagnóstico completado")

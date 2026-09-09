#!/usr/bin/env python
"""Verificar la configuración de Django"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from django.conf import settings

print('=== VERIFICACIÓN DE CONFIGURACIÓN ===\n')

# 1. Verificar ALLOWED_HOSTS
print('📋 ALLOWED_HOSTS:')
for host in settings.ALLOWED_HOSTS:
    print(f'  ✅ {host}')

# 2. Verificar CSRF_TRUSTED_ORIGINS
print('\n🔒 CSRF_TRUSTED_ORIGINS:')
if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
    for origin in settings.CSRF_TRUSTED_ORIGINS:
        print(f'  ✅ {origin}')
else:
    print('  ❌ CSRF_TRUSTED_ORIGINS no configurado')

# 3. Verificar directorio static
print('\n📁 Directorio static:')
if os.path.exists(settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else ''):
    print(f'  ✅ {settings.STATICFILES_DIRS[0]} existe')
else:
    print(f'  ❌ {settings.STATICFILES_DIRS[0]} no existe')

# 4. Verificar DEBUG
print(f'\n🐞 DEBUG: {settings.DEBUG}')

# 5. Recomendaciones
print('\n💡 RECOMENDACIONES:')
print('  1. Reinicia el servidor: python manage.py runserver')
print('  2. Limpia la caché del navegador: Ctrl+Shift+R')
print('  3. Accede a: http://localhost:8000/admin/')

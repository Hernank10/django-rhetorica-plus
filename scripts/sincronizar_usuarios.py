#!/usr/bin/env python
"""Sincronizar usuarios existentes entre auth.User y core.User"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from core.models import User as CoreUser

AuthUser = get_user_model()

print('=== SINCRONIZACIÓN DE USUARIOS ===\n')

sincronizados = 0
errores = 0

# 1. Sincronizar de auth.User a core.User
print('1. Sincronizando auth.User → core.User...')
for auth_user in AuthUser.objects.all():
    if not CoreUser.objects.filter(username=auth_user.username).exists():
        try:
            CoreUser.objects.create_user(
                username=auth_user.username,
                email=auth_user.email or f"{auth_user.username}@example.com",
                password=auth_user.password
            )
            print(f'  ✅ {auth_user.username} → core.User')
            sincronizados += 1
        except Exception as e:
            print(f'  ❌ Error con {auth_user.username}: {e}')
            errores += 1
    else:
        print(f'  ⏭️ {auth_user.username} ya existe en core.User')

# 2. Sincronizar de core.User a auth.User
print('\n2. Sincronizando core.User → auth.User...')
for core_user in CoreUser.objects.all():
    if not AuthUser.objects.filter(username=core_user.username).exists():
        try:
            AuthUser.objects.create_user(
                username=core_user.username,
                email=core_user.email or f"{core_user.username}@example.com",
                password=core_user.password
            )
            print(f'  ✅ {core_user.username} → auth.User')
            sincronizados += 1
        except Exception as e:
            print(f'  ❌ Error con {core_user.username}: {e}')
            errores += 1
    else:
        print(f'  ⏭️ {core_user.username} ya existe en auth.User')

print(f'\n📊 RESUMEN:')
print(f'  ✅ Usuarios sincronizados: {sincronizados}')
print(f'  ❌ Errores: {errores}')
print(f'  📈 Total auth.User: {AuthUser.objects.count()}')
print(f'  📈 Total core.User: {CoreUser.objects.count()}')

print('\n✅ Sincronización completada')

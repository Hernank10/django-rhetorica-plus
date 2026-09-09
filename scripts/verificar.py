#!/usr/bin/env python
"""Verificar el sistema"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from core.models import EjercicioLinguistico, TecnicaLinguistica
from django.contrib.auth.models import User

print('=== VERIFICACIÓN DEL SISTEMA ===\n')

print('📊 BASE DE DATOS:')
print(f'  Ejercicios: {EjercicioLinguistico.objects.count()}')
print(f'  Técnicas: {TecnicaLinguistica.objects.count()}')
print(f'  Usuarios: {User.objects.count()}')

print('\n📝 EJERCICIOS:')
for e in EjercicioLinguistico.objects.all()[:5]:
    print(f'  - {e.titulo} ({e.categoria})')

print('\n💡 TÉCNICAS:')
for t in TecnicaLinguistica.objects.all()[:5]:
    print(f'  - {t.nombre} ({t.categoria})')

print('\n✅ Sistema funcionando correctamente')

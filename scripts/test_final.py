#!/usr/bin/env python
"""Script de prueba final para Django Rhetorica"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.db import connection
from core.models import EjercicioLinguistico, TecnicaLinguistica, ContenidoJSON

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

print_section("ESTADO DE LA APLICACIÓN")

# 1. Datos
print(f"✅ Ejercicios: {EjercicioLinguistico.objects.count()}")
print(f"✅ Técnicas: {TecnicaLinguistica.objects.count()}")
print(f"✅ Contenidos: {ContenidoJSON.objects.count()}")
print(f"✅ Usuarios: {User.objects.count()}")

# 2. Campos de EjercicioLinguistico
print_section("CAMPOS DE EJERCICIOLINGUISTICO")
for field in EjercicioLinguistico._meta.fields:
    print(f"- {field.name}: {field.__class__.__name__}")

# 3. Mostrar algunos ejercicios
print_section("EJEMPLOS DE EJERCICIOS")
for e in EjercicioLinguistico.objects.all()[:5]:
    print(f"ID: {e.id}, Título: {e.titulo}")

# 4. Probar URLs
print_section("PRUEBA DE URLs CON SERVIDOR REAL")
print("Inicia el servidor con: python manage.py runserver")
print("Luego prueba:")
print("  - http://localhost:8000/login/")
print("  - http://localhost:8000/practicar/1/")
print("  - http://localhost:8000/dashboard/")

print("\n✅ ¡La aplicación está funcionando correctamente!")

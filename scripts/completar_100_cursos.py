#!/usr/bin/env python
"""Completar la generación de 100 cursos si faltan"""

import sys
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from core.models_cursos import Curso

total = Curso.objects.count()
print(f'Cursos actuales: {total}')

if total < 100:
    print(f'Faltan {100 - total} cursos. Ejecutando generador...')
    from scripts.generar_100_cursos import Generador100Cursos
    generador = Generador100Cursos()
    generador.cargar_datos()
    
    # Generar solo los que faltan
    for i in range(total + 1, 101):
        curso = generador.generar_curso(i)
        if i % 10 == 0:
            print(f'  ✅ Generados {i} cursos...')
    
    print(f'✅ Completados {Curso.objects.count()} cursos')
else:
    print('✅ Ya hay 100 cursos o más')

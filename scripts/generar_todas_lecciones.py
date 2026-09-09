#!/usr/bin/env python
"""Generar lecciones para todos los cursos"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from core.models import EjercicioLinguistico
from core.models_cursos import Curso, Modulo, Leccion

print('=== GENERANDO LECCIONES PARA TODOS LOS CURSOS ===\n')

ejercicios = list(EjercicioLinguistico.objects.all())
print(f'Total ejercicios: {len(ejercicios)}')

if len(ejercicios) == 0:
    print('❌ No hay ejercicios. Ejecuta: python scripts/generar_datos_prueba.py')
    exit()

cursos = Curso.objects.all()
print(f'Total cursos: {cursos.count()}\n')

for curso in cursos:
    print(f'📚 {curso.titulo}')
    
    # Verificar si ya tiene lecciones
    total_lecciones = 0
    for m in curso.modulos.all():
        total_lecciones += m.lecciones.count()
    
    if total_lecciones > 0:
        print(f'  ✅ Ya tiene {total_lecciones} lecciones')
        continue
    
    # Eliminar módulos vacíos
    for m in curso.modulos.all():
        m.delete()
    
    # Crear módulo
    modulo = Modulo.objects.create(
        curso=curso,
        titulo=f'Módulo 1: {curso.titulo[:30]}',
        descripcion=f'Lecciones de {curso.titulo}',
        orden=1
    )
    
    # Usar ejercicios de la misma categoría
    ejercicios_curso = []
    for ej in ejercicios:
        if ej.categoria and ej.categoria.lower() in curso.titulo.lower():
            ejercicios_curso.append(ej)
    
    if not ejercicios_curso:
        ejercicios_curso = ejercicios[:10]
    
    # Crear lecciones
    creadas = 0
    for i, ej in enumerate(ejercicios_curso[:10], 1):
        contenido = ej.contenido if isinstance(ej.contenido, dict) else {}
        leccion = Leccion.objects.create(
            modulo=modulo,
            titulo=ej.titulo or f'Lección {i}',
            contenido=contenido.get('teoria', 'Práctica de retórica'),
            tipo='practica',
            orden=i,
            duracion_estimada=15,
            puntos=ej.puntos or 10
        )
        leccion.ejercicios_relacionados.add(ej)
        creadas += 1
    
    print(f'  ✅ Creadas {creadas} lecciones')

print(f'\n✅ Proceso completado')

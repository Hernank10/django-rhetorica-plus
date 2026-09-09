#!/usr/bin/env python
"""Completar cursos que tienen 0 lecciones"""

import sys
import os
import random
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from core.models import EjercicioLinguistico, TecnicaLinguistica
from core.models_cursos import Curso, Modulo, Leccion, EvaluacionCurso, PreguntaEvaluacion

print('=== COMPLETANDO CURSOS VACÍOS ===\n')

# Obtener ejercicios
ejercicios = list(EjercicioLinguistico.objects.all())
print(f'📚 Ejercicios disponibles: {len(ejercicios)}')

if len(ejercicios) == 0:
    print('❌ No hay ejercicios')
    exit()

# Obtener técnicas
tecnicas = list(TecnicaLinguistica.objects.all())
print(f'💡 Técnicas disponibles: {len(tecnicas)}')

# Encontrar cursos vacíos
cursos_vacios = []
for curso in Curso.objects.all():
    lecciones = 0
    for m in curso.modulos.all():
        lecciones += m.lecciones.count()
    if lecciones == 0:
        cursos_vacios.append(curso)

print(f'\n📋 Cursos vacíos: {len(cursos_vacios)}')

if len(cursos_vacios) == 0:
    print('✅ Todos los cursos tienen lecciones')
    exit()

# Completar cada curso vacío
completados = 0
for curso in cursos_vacios:
    print(f'\n📝 Completando: {curso.titulo}')
    
    # Eliminar módulos existentes (si los hay)
    for m in curso.modulos.all():
        m.delete()
    
    # Seleccionar ejercicios para este curso
    ejercicios_curso = []
    for ej in ejercicios:
        if ej.categoria and ej.categoria.lower() in curso.titulo.lower():
            ejercicios_curso.append(ej)
    
    if len(ejercicios_curso) < 5:
        ejercicios_curso = random.sample(ejercicios, min(15, len(ejercicios)))
    
    # Crear módulos (3-5 por curso)
    num_modulos = random.randint(3, 5)
    ejercicios_por_modulo = max(3, len(ejercicios_curso) // num_modulos)
    
    for i in range(num_modulos):
        inicio = i * ejercicios_por_modulo
        fin = min((i + 1) * ejercicios_por_modulo, len(ejercicios_curso))
        ejercicios_modulo = ejercicios_curso[inicio:fin]
        
        if len(ejercicios_modulo) < 2:
            continue
        
        modulo = Modulo.objects.create(
            curso=curso,
            titulo=f"Módulo {i+1}: {curso.titulo[:30]} - Parte {i+1}",
            descripcion=f"Práctica y teoría de {curso.titulo[:40]}",
            orden=i+1
        )
        
        for j, ejercicio in enumerate(ejercicios_modulo, 1):
            contenido = ejercicio.contenido if isinstance(ejercicio.contenido, dict) else {}
            
            leccion = Leccion.objects.create(
                modulo=modulo,
                titulo=ejercicio.titulo or f"Lección {j}",
                contenido=contenido.get('teoria', f"Práctica de {curso.titulo[:30]}"),
                tipo='practica',
                orden=j,
                duracion_estimada=15,
                puntos=ejercicio.puntos or 10
            )
            leccion.ejercicios_relacionados.add(ejercicio)
            
            if tecnicas:
                tecnicas_aleatorias = random.sample(
                    tecnicas, 
                    min(random.randint(1, 2), len(tecnicas))
                )
                leccion.tecnicas_relacionadas.set(tecnicas_aleatorias)
    
    # Verificar lecciones creadas
    lecciones_creadas = 0
    for m in curso.modulos.all():
        lecciones_creadas += m.lecciones.count()
    
    if lecciones_creadas > 0:
        completados += 1
        print(f'  ✅ Creadas {lecciones_creadas} lecciones en {curso.modulos.count()} módulos')
    else:
        print(f'  ⚠️ No se pudieron crear lecciones para {curso.titulo}')

print(f'\n✅ Completados {completados} cursos vacíos')

# Mostrar resumen final
print('\n📊 RESUMEN FINAL:')
for curso in Curso.objects.all()[:10]:
    lecciones = 0
    for m in curso.modulos.all():
        lecciones += m.lecciones.count()
    print(f'  - {curso.titulo[:40]}... {lecciones} lecciones')

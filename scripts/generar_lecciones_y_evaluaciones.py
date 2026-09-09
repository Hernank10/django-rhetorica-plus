#!/usr/bin/env python
"""Generar lecciones y evaluaciones para todos los cursos desde ejercicios existentes"""

import sys
import os
import random
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from core.models import EjercicioLinguistico
from core.models_cursos import Curso, Modulo, Leccion, EvaluacionCurso, PreguntaEvaluacion

print('=== GENERANDO LECCIONES Y EVALUACIONES ===\n')

# Obtener ejercicios
ejercicios = list(EjercicioLinguistico.objects.all())
print(f'📚 Ejercicios disponibles: {len(ejercicios)}')

if len(ejercicios) == 0:
    print('❌ No hay ejercicios. Ejecuta: python scripts/generar_datos_prueba.py')
    exit()

# Obtener cursos
cursos = Curso.objects.all()
print(f'📚 Cursos encontrados: {cursos.count()}\n')

for curso in cursos:
    print(f'📝 Procesando: {curso.titulo}')
    
    # 1. Verificar y generar lecciones
    total_lecciones = 0
    modulos_existentes = list(curso.modulos.all())
    
    for m in modulos_existentes:
        total_lecciones += m.lecciones.count()
    
    if total_lecciones == 0:
        print('  ⚠️ Sin lecciones. Generando...')
        
        # Eliminar módulos vacíos
        for m in modulos_existentes:
            m.delete()
        
        # Seleccionar ejercicios para este curso
        ejercicios_curso = []
        for ej in ejercicios:
            if ej.categoria and ej.categoria.lower() in curso.titulo.lower():
                ejercicios_curso.append(ej)
        
        if not ejercicios_curso:
            ejercicios_curso = ejercicios[:10]
        
        # Limitar a 10 ejercicios
        ejercicios_curso = ejercicios_curso[:10]
        
        # Crear módulo
        modulo = Modulo.objects.create(
            curso=curso,
            titulo=f"Módulo 1: {curso.titulo[:30]}",
            descripcion=f"Lecciones de {curso.titulo}",
            orden=1
        )
        
        # Crear lecciones
        for i, ej in enumerate(ejercicios_curso, 1):
            contenido = ej.contenido if isinstance(ej.contenido, dict) else {}
            leccion = Leccion.objects.create(
                modulo=modulo,
                titulo=ej.titulo or f"Lección {i}",
                contenido=contenido.get('teoria', f"Práctica de {curso.titulo}"),
                tipo='practica',
                orden=i,
                duracion_estimada=15,
                puntos=ej.puntos or 10
            )
            leccion.ejercicios_relacionados.add(ej)
        
        print(f'  ✅ Creadas {len(ejercicios_curso)} lecciones')
    else:
        print(f'  ✅ Ya tiene {total_lecciones} lecciones')
    
    # 2. Verificar y generar evaluaciones
    evaluaciones_existentes = EvaluacionCurso.objects.filter(curso=curso)
    
    if evaluaciones_existentes.count() == 0:
        print('  ⚠️ Sin evaluaciones. Generando...')
        
        # Obtener lecciones del curso
        lecciones = []
        for m in curso.modulos.all():
            lecciones.extend(m.lecciones.all())
        
        if not lecciones:
            print('  ⚠️ No hay lecciones para crear evaluación')
            continue
        
        # Obtener ejercicios de las lecciones
        ejercicios_eval = []
        for lec in lecciones:
            ejercicios_eval.extend(lec.ejercicios_relacionados.all())
        
        if not ejercicios_eval:
            ejercicios_eval = ejercicios[:10]
        
        # Crear evaluación
        evaluacion = EvaluacionCurso.objects.create(
            curso=curso,
            titulo=f"Evaluación de {curso.titulo}",
            descripcion=f"Evalúa tus conocimientos en {curso.titulo}",
            tipo='sumativa',
            preguntas_por_evaluacion=min(10, len(ejercicios_eval)),
            tiempo_limite=30,
            puntaje_maximo=0,
            intentos_permitidos=3,
            disponible_desde=datetime.now(),
            disponible_hasta=datetime.now() + timedelta(days=30)
        )
        
        # Crear preguntas
        puntaje_total = 0
        preguntas_creadas = 0
        for i, ej in enumerate(ejercicios_eval[:10], 1):
            contenido = ej.contenido if isinstance(ej.contenido, dict) else {}
            
            pregunta = PreguntaEvaluacion.objects.create(
                evaluacion=evaluacion,
                ejercicio=ej,
                enunciado=contenido.get('ejercicio', f"Ejercicio {i}"),
                tipo='desarrollo',
                respuesta_correcta=contenido.get('suggestedAnswer', ''),
                puntaje=10,
                orden=i
            )
            puntaje_total += 10
            preguntas_creadas += 1
        
        evaluacion.puntaje_maximo = puntaje_total
        evaluacion.save()
        
        print(f'  ✅ Creada evaluación con {preguntas_creadas} preguntas')
    else:
        print(f'  ✅ Ya tiene {evaluaciones_existentes.count()} evaluaciones')
    
    print()

print('✅ Proceso completado')

# Mostrar resumen final
print('\n📊 RESUMEN FINAL:')
for curso in Curso.objects.all():
    lecciones = 0
    for m in curso.modulos.all():
        lecciones += m.lecciones.count()
    evaluaciones = EvaluacionCurso.objects.filter(curso=curso).count()
    preguntas = 0
    for e in EvaluacionCurso.objects.filter(curso=curso):
        preguntas += PreguntaEvaluacion.objects.filter(evaluacion=e).count()
    print(f'  ✅ {curso.titulo[:30]}... - {lecciones} lecciones, {evaluaciones} evaluaciones, {preguntas} preguntas')

#!/usr/bin/env python
"""Generar evaluaciones para todos los cursos directamente"""

import sys
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from core.models import EjercicioLinguistico
from core.models_cursos import Curso, Modulo, Leccion, EvaluacionCurso, PreguntaEvaluacion

print('=== GENERANDO EVALUACIONES PARA TODOS LOS CURSOS ===\n')

# Obtener ejercicios
ejercicios = list(EjercicioLinguistico.objects.all())
print(f'📚 Ejercicios disponibles: {len(ejercicios)}')

if len(ejercicios) == 0:
    print('❌ No hay ejercicios. Ejecuta: python scripts/generar_datos_prueba.py')
    exit()

# Obtener cursos
cursos = Curso.objects.filter(estado='publicado')
print(f'📚 Cursos encontrados: {cursos.count()}\n')

for curso in cursos:
    print(f'📝 Procesando: {curso.titulo}')
    
    # Verificar si ya tiene evaluaciones
    evaluaciones_existentes = EvaluacionCurso.objects.filter(curso=curso)
    if evaluaciones_existentes.count() > 0:
        print(f'  ✅ Ya tiene {evaluaciones_existentes.count()} evaluaciones')
        continue
    
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

print('\n✅ Proceso completado')

# Mostrar resumen
print('\n📊 RESUMEN FINAL:')
for curso in Curso.objects.all():
    evaluaciones = EvaluacionCurso.objects.filter(curso=curso).count()
    preguntas = 0
    for e in EvaluacionCurso.objects.filter(curso=curso):
        preguntas += PreguntaEvaluacion.objects.filter(evaluacion=e).count()
    print(f'  ✅ {curso.titulo[:30]}... - {evaluaciones} evaluaciones, {preguntas} preguntas')

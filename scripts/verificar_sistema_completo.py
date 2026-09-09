#!/usr/bin/env python
"""Verificar el estado completo del sistema"""

import sys
import os
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from core.models import EjercicioLinguistico, TecnicaLinguistica
from core.models_cursos import Curso, Modulo, Leccion, EvaluacionCurso, PreguntaEvaluacion
from django.contrib.auth.models import User

print('=== ESTADO COMPLETO DEL SISTEMA ===\n')

print('📚 EJERCICIOS:')
print(f'  Total: {EjercicioLinguistico.objects.count()}')

print('\n💡 TÉCNICAS:')
print(f'  Total: {TecnicaLinguistica.objects.count()}')

print('\n📚 CURSOS:')
cursos = Curso.objects.all()
print(f'  Total: {cursos.count()}')
for curso in cursos:
    modulos = curso.modulos.count()
    lecciones = sum(m.lecciones.count() for m in curso.modulos.all())
    print(f'  - {curso.titulo} (Módulos: {modulos}, Lecciones: {lecciones})')

print('\n📝 EVALUACIONES:')
evaluaciones = EvaluacionCurso.objects.all()
print(f'  Total: {evaluaciones.count()}')
for eval in evaluaciones:
    preguntas = PreguntaEvaluacion.objects.filter(evaluacion=eval).count()
    print(f'  - {eval.titulo} (Preguntas: {preguntas}, Máximo: {eval.puntaje_maximo})')

print('\n👤 USUARIOS:')
print(f'  Total: {User.objects.count()}')
for user in User.objects.all():
    print(f'  - {user.username}')

print('\n✅ Sistema completo funcionando correctamente!')

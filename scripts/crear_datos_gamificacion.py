import os
import sys
import django

sys.path.append('/workspaces/django-rhetorica-plus')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
django.setup()

from core.models import Logro, Evaluacion

# Crear logros
logros = [
    {'nombre': 'Primeros Pasos', 'descripcion': 'Completa tu primer ejercicio', 'tipo': 'insignia', 'icono': '🌟', 'puntos_requeridos': 10},
    {'nombre': 'Aprendiz Dedicado', 'descripcion': 'Completa 10 ejercicios', 'tipo': 'insignia', 'icono': '📚', 'puntos_requeridos': 50},
    {'nombre': 'Maestro de la Retórica', 'descripcion': 'Alcanza 1000 puntos', 'tipo': 'medalla', 'icono': '🏆', 'puntos_requeridos': 1000},
    {'nombre': 'Experto en Gramática', 'descripcion': 'Completa 50 ejercicios de gramática', 'tipo': 'certificacion', 'icono': '📜', 'puntos_requeridos': 300},
    {'nombre': 'Estrella Brillante', 'descripcion': 'Obtén 5 estrellas', 'tipo': 'estrella', 'icono': '⭐', 'puntos_requeridos': 500},
]

for logro_data in logros:
    Logro.objects.get_or_create(
        nombre=logro_data['nombre'],
        defaults={
            'descripcion': logro_data['descripcion'],
            'tipo': logro_data['tipo'],
            'icono': logro_data['icono'],
            'puntos_requeridos': logro_data['puntos_requeridos'],
        }
    )
    print(f"✅ Logro creado: {logro_data['nombre']}")

# Crear evaluaciones de ejemplo
evaluaciones = [
    {
        'titulo': 'Evaluación de Gramática Básica',
        'descripcion': 'Prueba tus conocimientos básicos de gramática española',
        'tipo': 'diagnostico',
        'categoria': 'Gramática',
        'nivel_requerido': 1,
        'puntos_base': 10,
        'duracion_minutos': 15,
        'preguntas': [
            {'texto': '¿Cuál es el sujeto en "El perro corre rápidamente"?', 'opciones': ['El perro', 'corre', 'rápidamente', 'ninguna']},
            {'texto': '¿Qué tipo de palabra es "rápidamente"?', 'opciones': ['Adjetivo', 'Adverbio', 'Sustantivo', 'Verbo']},
        ]
    },
    {
        'titulo': 'Evaluación de Retórica Avanzada',
        'descripcion': 'Demuestra tu dominio de las figuras retóricas',
        'tipo': 'sumativa',
        'categoria': 'Retórica',
        'nivel_requerido': 2,
        'puntos_base': 20,
        'duracion_minutos': 30,
        'preguntas': [
            {'texto': '¿Qué figura retórica compara dos elementos usando "como"?', 'opciones': ['Metáfora', 'Símil', 'Hipérbole', 'Personificación']},
            {'texto': '¿Qué es una metáfora?', 'opciones': ['Comparación directa', 'Exageración', 'Atribuir cualidades humanas', 'Ninguna']},
        ]
    },
]

for eval_data in evaluaciones:
    Evaluacion.objects.get_or_create(
        titulo=eval_data['titulo'],
        defaults={
            'descripcion': eval_data['descripcion'],
            'tipo': eval_data['tipo'],
            'categoria': eval_data['categoria'],
            'nivel_requerido': eval_data['nivel_requerido'],
            'puntos_base': eval_data['puntos_base'],
            'duracion_minutos': eval_data['duracion_minutos'],
            'preguntas': eval_data['preguntas'],
            'activa': True,
        }
    )
    print(f"✅ Evaluación creada: {eval_data['titulo']}")

print("\n🎮 ¡Datos de gamificación creados exitosamente!")

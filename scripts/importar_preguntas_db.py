#!/usr/bin/env python
"""Importar preguntas generadas a la base de datos"""

import os
import sys
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from core.models_preguntas import PreguntaGenerada
from django.contrib.auth.models import User

def importar_preguntas(archivo_json):
    """Importar preguntas desde JSON"""
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        preguntas = data.get('preguntas', [])
        
        # Obtener usuario admin
        usuario = User.objects.first()
        
        importadas = 0
        for p in preguntas:
            # Verificar si ya existe
            if PreguntaGenerada.objects.filter(
                titulo=p.get('titulo', ''),
                tipo=p.get('tipo', '')
            ).exists():
                continue
            
            PreguntaGenerada.objects.create(
                tipo=p.get('tipo', 'desarrollo'),
                titulo=p.get('titulo', 'Sin título'),
                enunciado=p.get('enunciado', ''),
                respuesta_correcta=p.get('respuesta_correcta', ''),
                opciones=p.get('opciones', None),
                pista=p.get('pista', ''),
                dificultad=p.get('dificultad', 1),
                puntos=p.get('puntos', 10),
                categoria=p.get('categoria', ''),
                ejercicio_base_id=p.get('ejercicio_base_id'),
                creado_por=usuario,
                activa=True,
            )
            importadas += 1
        
        print(f'✅ {importadas} preguntas importadas de {len(preguntas)} totales')
        return importadas
    except Exception as e:
        print(f'❌ Error: {e}')
        return 0

if __name__ == "__main__":
    # Buscar el archivo más reciente
    import glob
    archivos = glob.glob('preguntas_generadas_*.json')
    if archivos:
        archivo = sorted(archivos)[-1]
        print(f'📂 Importando desde: {archivo}')
        importar_preguntas(archivo)
    else:
        print('❌ No se encontraron archivos JSON')

#!/usr/bin/env python
"""
Extraer ejercicios desde la API y guardarlos en JSON
Ejecuta: python extraer_api_ejercicios.py
"""

import os
import sys
import json
import requests
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from core.models import EjercicioLinguistico

def extraer_ejercicios():
    """Extraer ejercicios de la base de datos y guardarlos en JSON"""
    
    print("📤 Extrayendo ejercicios de la base de datos...")
    
    ejercicios = EjercicioLinguistico.objects.all()
    datos = []
    
    for e in ejercicios:
        # Procesar contenido
        contenido = e.contenido
        if isinstance(contenido, str):
            try:
                contenido = json.loads(contenido)
            except:
                contenido = {'teoria': contenido}
        
        datos.append({
            'id': e.id,
            'titulo': e.titulo,
            'categoria': e.categoria,
            'tipo': e.tipo,
            'nivel': e.nivel,
            'puntos': e.puntos,
            'contenido': contenido if isinstance(contenido, dict) else {'teoria': str(contenido)}
        })
    
    # Guardar en archivo
    fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f'ejercicios_exportados_{fecha}.json'
    
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Exportados {len(datos)} ejercicios a {nombre_archivo}")
    return nombre_archivo

if __name__ == "__main__":
    extraer_ejercicios()

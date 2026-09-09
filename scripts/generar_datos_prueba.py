#!/usr/bin/env python
"""
Generador de datos de prueba para Rhetorica Plus
Ejecuta: python scripts/generar_datos_prueba.py
"""

import sys
import os

# Configurar Django - IMPORTANTE para scripts en scripts/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from core.models import EjercicioLinguistico, TecnicaLinguistica
from django.contrib.auth.models import User

class Color:
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    CYAN = '\033[96m'
    NEGRITA = '\033[1m'
    FIN = '\033[0m'

def generar_ejercicios():
    """Generar ejercicios de prueba"""
    ejercicios_existentes = EjercicioLinguistico.objects.count()
    
    if ejercicios_existentes >= 10:
        print(f"{Color.VERDE}✅ Ya hay {ejercicios_existentes} ejercicios{Color.FIN}")
        return
    
    print(f"{Color.AMARILLO}⚠️ Generando ejercicios de prueba...{Color.FIN}")
    
    ejercicios = [
        {
            "titulo": "Uso de 'acorde'",
            "categoria": "Gramatica",
            "tipo": "General",
            "nivel": 1,
            "puntos": 10,
            "contenido": {
                "teoria": "'Acorde' significa 'conforme' y puede usarse como adjetivo invariable o seguido de 'con'.",
                "ejemplo": "Una actuación acorde a las normas.",
                "ejercicio": "Corrige: 'Debe actuar acorde las reglas'.",
                "suggestedAnswer": "Debe actuar acorde con las reglas"
            }
        },
        {
            "titulo": "Uso de 'aplicar'",
            "categoria": "Gramatica",
            "tipo": "General",
            "nivel": 1,
            "puntos": 10,
            "contenido": {
                "teoria": "Se aplica una cosa 'a' alguien o algo.",
                "ejemplo": "Aplicaron la vacuna a los niños.",
                "ejercicio": "Completa: 'Debemos aplicar la normativa ___ todos'.",
                "suggestedAnswer": "a"
            }
        },
        {
            "titulo": "Uso de 'demás'",
            "categoria": "Gramatica",
            "tipo": "General",
            "nivel": 1,
            "puntos": 10,
            "contenido": {
                "teoria": "'Demás' equivale a 'otros' o 'los restantes'.",
                "ejemplo": "Los demás están de acuerdo.",
                "ejercicio": "Reemplaza 'otros': 'Otros vinieron tarde'.",
                "suggestedAnswer": "Los demás vinieron tarde"
            }
        },
        {
            "titulo": "Uso de 'mismo'",
            "categoria": "Gramatica",
            "tipo": "General",
            "nivel": 1,
            "puntos": 10,
            "contenido": {
                "teoria": "Puede usarse 'mismo' para dar énfasis.",
                "ejemplo": "Usted mismo lo dijo.",
                "ejercicio": "Escribe una frase con 'mismo' en primera persona.",
                "suggestedAnswer": "Yo mismo resolveré el problema"
            }
        },
        {
            "titulo": "Uso de 'cualquiera'",
            "categoria": "Gramatica",
            "tipo": "General",
            "nivel": 1,
            "puntos": 10,
            "contenido": {
                "teoria": "'Cualquier' se usa ante sustantivo.",
                "ejemplo": "Cualquier persona puede venir.",
                "ejercicio": "Completa: '___ estudiante puede participar'.",
                "suggestedAnswer": "Cualquier"
            }
        }
    ]
    
    for data in ejercicios:
        EjercicioLinguistico.objects.create(**data)
    
    print(f"{Color.VERDE}✅ Generados {len(ejercicios)} ejercicios{Color.FIN}")

def generar_tecnicas():
    """Generar técnicas de prueba"""
    if TecnicaLinguistica.objects.count() >= 3:
        return
    
    print(f"{Color.AMARILLO}⚠️ Generando técnicas de prueba...{Color.FIN}")
    
    tecnicas = [
        {'nombre': 'Metáfora', 'descripcion': 'Comparación implícita entre dos elementos', 'categoria': 'Figuras Retóricas'},
        {'nombre': 'Anáfora', 'descripcion': 'Repetición de palabras al inicio de versos', 'categoria': 'Figuras Retóricas'},
        {'nombre': 'Hipérbole', 'descripcion': 'Exageración para enfatizar una idea', 'categoria': 'Figuras Retóricas'},
        {'nombre': 'Ironía', 'descripcion': 'Decir lo contrario de lo que se piensa', 'categoria': 'Figuras Retóricas'},
        {'nombre': 'Sinécdoque', 'descripcion': 'Designar el todo por la parte o viceversa', 'categoria': 'Tropos'},
    ]
    
    for t in tecnicas:
        TecnicaLinguistica.objects.create(**t)
    
    print(f"{Color.VERDE}✅ Generadas {len(tecnicas)} técnicas{Color.FIN}")

def main():
    print(f"\n{Color.CYAN}{'='*60}{Color.FIN}")
    print(f"{Color.NEGRITA}🚀 GENERADOR DE DATOS DE PRUEBA{Color.FIN}")
    print(f"{Color.CYAN}{'='*60}{Color.FIN}")
    print(f"📂 Directorio raíz: {BASE_DIR}\n")
    
    generar_ejercicios()
    generar_tecnicas()
    
    # Mostrar estadísticas
    print(f"\n{Color.VERDE}📊 ESTADÍSTICAS FINALES:{Color.FIN}")
    print(f"  ✅ Ejercicios: {EjercicioLinguistico.objects.count()}")
    print(f"  ✅ Técnicas: {TecnicaLinguistica.objects.count()}")
    print(f"  ✅ Usuarios: {User.objects.count()}")
    
    print(f"\n{Color.AZUL}💡 PRÓXIMOS PASOS:{Color.FIN}")
    print(f"  1. Inicia el servidor: python manage.py runserver")
    print(f"  2. Accede al dashboard: http://localhost:8000/dashboard/")
    print(f"  3. Ver ejercicios: http://localhost:8000/biblioteca/")
    print(f"  4. Ver técnicas: http://localhost:8000/tecnicas/")
    
    print(f"\n{Color.VERDE}✅ ¡Listo!{Color.FIN}")

if __name__ == "__main__":
    main()

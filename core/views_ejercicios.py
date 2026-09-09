"""Vistas para mostrar ejercicios correctamente"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import EjercicioLinguistico

@login_required
def detalle_ejercicio(request, ejercicio_id):
    """Vista para mostrar un ejercicio con su contenido completo"""
    ejercicio = get_object_or_404(EjercicioLinguistico, id=ejercicio_id)
    
    # El contenido ya es un diccionario
    contenido = ejercicio.contenido
    if not isinstance(contenido, dict):
        contenido = {
            'teoria': str(contenido) if contenido else 'Sin teoría',
            'ejercicio': 'Sin ejercicio',
            'suggestedAnswer': 'Sin respuesta sugerida'
        }
    
    context = {
        'ejercicio': ejercicio,
        'contenido': contenido,
    }
    
    return render(request, 'core/detalle_ejercicio.html', context)

@login_required
def practicar_ejercicio(request, ejercicio_id):
    """Vista para practicar un ejercicio"""
    ejercicio = get_object_or_404(EjercicioLinguistico, id=ejercicio_id)
    
    contenido = ejercicio.contenido
    if not isinstance(contenido, dict):
        contenido = {
            'teoria': str(contenido) if contenido else 'Sin teoría',
            'ejercicio': 'Sin ejercicio',
            'suggestedAnswer': 'Sin respuesta sugerida'
        }
    
    context = {
        'ejercicio': ejercicio,
        'contenido': contenido,
    }
    
    return render(request, 'core/practicar_ejercicio.html', context)

@login_required
def api_ejercicio_detalle(request, ejercicio_id):
    """API para obtener detalles de un ejercicio en JSON"""
    ejercicio = get_object_or_404(EjercicioLinguistico, id=ejercicio_id)
    
    data = {
        'id': ejercicio.id,
        'titulo': ejercicio.titulo,
        'categoria': ejercicio.categoria,
        'tipo': ejercicio.tipo,
        'nivel': ejercicio.nivel,
        'puntos': ejercicio.puntos,
        'contenido': ejercicio.contenido,  # Ya es un dict
    }
    
    return JsonResponse(data)

"""Vistas actualizadas para usar los nuevos templates"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import EjercicioLinguistico

@login_required
def detalle_ejercicio_completo(request, ejercicio_id):
    """Vista detallada con template completo"""
    ejercicio = get_object_or_404(EjercicioLinguistico, id=ejercicio_id)
    
    # Procesar contenido
    contenido = ejercicio.contenido if isinstance(ejercicio.contenido, dict) else {}
    
    context = {
        'ejercicio': ejercicio,
        'contenido': contenido,
        'ejercicio_id': ejercicio.id,
    }
    return render(request, 'core/detalle_ejercicio_completo.html', context)

@login_required
def practicar_ejercicio_completo(request, ejercicio_id):
    """Vista para practicar con template completo"""
    ejercicio = get_object_or_404(EjercicioLinguistico, id=ejercicio_id)
    
    contenido = ejercicio.contenido if isinstance(ejercicio.contenido, dict) else {}
    
    context = {
        'ejercicio': ejercicio,
        'contenido': contenido,
        'ejercicio_id': ejercicio.id,
    }
    return render(request, 'core/practicar_ejercicio_completo.html', context)

@login_required
def lista_ejercicios(request):
    """Lista de todos los ejercicios con filtros"""
    ejercicios = EjercicioLinguistico.objects.all()
    
    # Filtros
    categoria = request.GET.get('categoria', '')
    nivel = request.GET.get('nivel', '')
    tipo = request.GET.get('tipo', '')
    
    if categoria:
        ejercicios = ejercicios.filter(categoria=categoria)
    if nivel:
        ejercicios = ejercicios.filter(nivel=int(nivel))
    if tipo:
        ejercicios = ejercicios.filter(tipo=tipo)
    
    # Obtener categorías para el filtro
    categorias = EjercicioLinguistico.objects.values_list('categoria', flat=True).distinct()
    
    # Paginación
    paginator = Paginator(ejercicios, 12)
    page = request.GET.get('page', 1)
    ejercicios_page = paginator.get_page(page)
    
    context = {
        'ejercicios': ejercicios_page,
        'categorias': categorias,
        'categoria_seleccionada': categoria,
        'nivel_seleccionado': nivel,
        'tipo_seleccionado': tipo,
        'is_paginated': ejercicios_page.has_other_pages(),
        'page_obj': ejercicios_page,
    }
    return render(request, 'core/lista_ejercicios.html', context)

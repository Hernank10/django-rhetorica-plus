"""Vista para mostrar ejercicios desde la API en un template"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import EjercicioLinguistico

@login_required
def ejercicios_template_view(request):
    """Vista que obtiene ejercicios y los organiza por categorías"""
    
    # Obtener todos los ejercicios
    ejercicios = EjercicioLinguistico.objects.all()
    
    # Agrupar por categoría
    categorias = {}
    categorias_list = []
    
    for ejercicio in ejercicios:
        categoria = ejercicio.categoria or 'Sin categoría'
        if categoria not in categorias:
            categorias[categoria] = []
            categorias_list.append(categoria)
        categorias[categoria].append(ejercicio)
    
    # Preparar datos para el template
    categorias_data = []
    for cat in categorias_list:
        categorias_data.append({
            'nombre': cat,
            'ejercicios': categorias[cat],
            'total': len(categorias[cat])
        })
    
    # Estadísticas
    total_ejercicios = len(ejercicios)
    total_categorias = len(categorias_list)
    
    # Obtener ejercicios destacados (aleatorios) para mostrar
    destacados = ejercicios.order_by('?')[:6] if ejercicios else []
    
    context = {
        'categorias': categorias_data,
        'total_ejercicios': total_ejercicios,
        'total_categorias': total_categorias,
        'destacados': destacados,
        'ejercicios': ejercicios,
    }
    
    return render(request, 'core/ejercicios_template.html', context)

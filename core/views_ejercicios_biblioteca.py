"""Vista para la biblioteca de ejercicios"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import EjercicioLinguistico

@login_required
def ejercicios_biblioteca(request):
    """Vista que muestra todos los ejercicios en formato de biblioteca"""
    
    ejercicios = EjercicioLinguistico.objects.all().order_by('categoria', 'titulo')
    
    # Obtener categorías únicas
    categorias = EjercicioLinguistico.objects.values_list('categoria', flat=True).distinct()
    categorias = [c for c in categorias if c]  # Eliminar None/empty
    
    context = {
        'ejercicios': ejercicios,
        'categorias': categorias,
        'total_ejercicios': ejercicios.count(),
        'total_categorias': len(categorias),
    }
    
    return render(request, 'core/ejercicios_biblioteca.html', context)

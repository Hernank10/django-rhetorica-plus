"""Vistas de API para ejercicios"""

import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import EjercicioLinguistico

@login_required
def ejercicios_json(request):
    """API para obtener todos los ejercicios en JSON"""
    ejercicios = EjercicioLinguistico.objects.all()
    
    data = []
    for ejercicio in ejercicios:
        # Procesar contenido
        contenido = ejercicio.contenido
        if isinstance(contenido, str):
            try:
                contenido = json.loads(contenido)
            except:
                contenido = {}
        
        data.append({
            'id': ejercicio.id,
            'titulo': ejercicio.titulo,
            'categoria': ejercicio.categoria,
            'tipo': ejercicio.tipo,
            'nivel': ejercicio.nivel,
            'puntos': ejercicio.puntos,
            'contenido': contenido if isinstance(contenido, dict) else {}
        })
    
    return JsonResponse(data, safe=False)

@login_required
def ejercicio_detalle_json(request, ejercicio_id):
    """API para obtener un ejercicio específico"""
    ejercicio = EjercicioLinguistico.objects.get(id=ejercicio_id)
    
    contenido = ejercicio.contenido
    if isinstance(contenido, str):
        try:
            contenido = json.loads(contenido)
        except:
            contenido = {}
    
    data = {
        'id': ejercicio.id,
        'titulo': ejercicio.titulo,
        'categoria': ejercicio.categoria,
        'tipo': ejercicio.tipo,
        'nivel': ejercicio.nivel,
        'puntos': ejercicio.puntos,
        'contenido': contenido if isinstance(contenido, dict) else {}
    }
    
    return JsonResponse(data)

@login_required
def tecnicas_json(request):
    """API para obtener técnicas"""
    from .models import TecnicaLinguistica
    tecnicas = TecnicaLinguistica.objects.all()
    
    data = [{
        'id': t.id,
        'nombre': t.nombre,
        'descripcion': t.descripcion,
        'categoria': t.categoria
    } for t in tecnicas]
    
    return JsonResponse(data, safe=False)

@login_required
def contenidos_json(request):
    """API para obtener contenidos"""
    from .models import ContenidoJSON
    contenidos = ContenidoJSON.objects.all()
    
    data = [{
        'id': c.id,
        'titulo': c.titulo,
        'descripcion': c.descripcion,
        'contenido': c.contenido,
        'tipo': c.tipo
    } for c in contenidos]
    
    return JsonResponse(data, safe=False)

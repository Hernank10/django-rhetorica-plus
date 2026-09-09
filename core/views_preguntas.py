"""
Vistas para gestionar preguntas generadas
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
import json
import random

from .models_preguntas import PreguntaGenerada, RespuestaPregunta
from .models import EjercicioLinguistico

@login_required
def ver_preguntas(request):
    """Ver todas las preguntas generadas"""
    tipo_filtro = request.GET.get('tipo', '')
    dificultad_filtro = request.GET.get('dificultad', '')
    
    preguntas = PreguntaGenerada.objects.filter(activa=True)
    
    if tipo_filtro:
        preguntas = preguntas.filter(tipo=tipo_filtro)
    if dificultad_filtro:
        preguntas = preguntas.filter(dificultad=dificultad_filtro)
    
    paginator = Paginator(preguntas, 20)
    page = request.GET.get('page', 1)
    preguntas_page = paginator.get_page(page)
    
    context = {
        'preguntas': preguntas_page,
        'tipos': PreguntaGenerada.TIPOS_PREGUNTA,
        'niveles': PreguntaGenerada.NIVELES_DIFICULTAD,
        'tipo_seleccionado': tipo_filtro,
        'dificultad_seleccionada': dificultad_filtro,
    }
    return render(request, 'core/preguntas/lista.html', context)

@login_required
def practicar_pregunta(request, pregunta_id):
    """Practicar una pregunta específica"""
    pregunta = get_object_or_404(PreguntaGenerada, id=pregunta_id, activa=True)
    
    context = {
        'pregunta': pregunta,
        'contenido': {
            'teoria': pregunta.pista,
            'ejercicio': pregunta.enunciado,
            'suggestedAnswer': pregunta.respuesta_correcta,
        },
        'ejercicio': type('obj', (object,), {
            'id': pregunta.id,
            'titulo': pregunta.titulo,
            'categoria': pregunta.categoria,
            'nivel': pregunta.dificultad,
            'puntos': pregunta.puntos,
        }),
    }
    return render(request, 'core/practicar_pregunta.html', context)

@login_required
def generar_preguntas_desde_bd(request):
    """Generar preguntas desde la base de datos existente"""
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 10))
        tipos = request.POST.getlist('tipos')
        
        from generar_preguntas_v2 import GeneradorPreguntas
        generador = GeneradorPreguntas()
        preguntas_generadas = generador.generar_100_preguntas()
        
        # Guardar en la base de datos
        guardadas = 0
        for p in preguntas_generadas[:cantidad]:
            if tipos and p['tipo'] not in tipos:
                continue
                
            PreguntaGenerada.objects.create(
                tipo=p['tipo'],
                titulo=p['titulo'],
                enunciado=p['enunciado'],
                respuesta_correcta=p['respuesta_correcta'],
                pista=p.get('pista', ''),
                dificultad=p.get('dificultad', 1),
                puntos=p.get('puntos', 10),
                categoria=p.get('categoria', ''),
                ejercicio_base_id=p.get('ejercicio_base_id'),
                creado_por=request.user,
                activa=True,
            )
            guardadas += 1
        
        return JsonResponse({
            'success': True,
            'guardadas': guardadas,
            'total': len(preguntas_generadas)
        })
    
    context = {
        'tipos': PreguntaGenerada.TIPOS_PREGUNTA,
    }
    return render(request, 'core/preguntas/generar.html', context)

@login_required
def api_pregunta_aleatoria(request):
    """API para obtener una pregunta aleatoria"""
    tipo = request.GET.get('tipo', '')
    dificultad = request.GET.get('dificultad', '')
    
    preguntas = PreguntaGenerada.objects.filter(activa=True)
    
    if tipo:
        preguntas = preguntas.filter(tipo=tipo)
    if dificultad:
        preguntas = preguntas.filter(dificultad=dificultad)
    
    if not preguntas.exists():
        return JsonResponse({'error': 'No hay preguntas disponibles'}, status=404)
    
    pregunta = random.choice(preguntas)
    
    # Marcar como usada
    pregunta.usado_en += 1
    pregunta.save()
    
    return JsonResponse({
        'id': pregunta.id,
        'tipo': pregunta.tipo,
        'titulo': pregunta.titulo,
        'enunciado': pregunta.enunciado,
        'respuesta_correcta': pregunta.respuesta_correcta,
        'opciones': pregunta.opciones,
        'dificultad': pregunta.dificultad,
        'puntos': pregunta.puntos,
        'categoria': pregunta.categoria,
        'pista': pregunta.pista,
    })

@login_required
def api_evaluar_respuesta(request, pregunta_id):
    """API para evaluar una respuesta"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    pregunta = get_object_or_404(PreguntaGenerada, id=pregunta_id)
    respuesta_usuario = request.POST.get('respuesta', '').strip()
    
    # Evaluar según tipo
    es_correcta = False
    if pregunta.tipo in ['correccion', 'completar', 'reescribir', 'elegir']:
        # Comparación simple
        es_correcta = respuesta_usuario.lower() == pregunta.respuesta_correcta.lower()
    elif pregunta.tipo == 'verdadero_falso':
        es_correcta = respuesta_usuario.lower() in ['verdadero', 'verdad'] and pregunta.respuesta_correcta.lower() == 'verdadero'
        if not es_correcta:
            es_correcta = respuesta_usuario.lower() in ['falso', 'fals'] and pregunta.respuesta_correcta.lower() == 'falso'
    elif pregunta.tipo == 'multiple_choice':
        es_correcta = respuesta_usuario == pregunta.opciones[0] if pregunta.opciones else False
    else:
        # Para tipos de respuesta abierta, solo guardamos
        es_correcta = True  # Se evaluará manualmente
    
    # Guardar respuesta
    respuesta_obj, creada = RespuestaPregunta.objects.update_or_create(
        pregunta=pregunta,
        usuario=request.user,
        defaults={
            'respuesta': respuesta_usuario,
            'es_correcta': es_correcta,
            'puntos_obtenidos': pregunta.puntos if es_correcta else 0,
        }
    )
    
    return JsonResponse({
        'es_correcta': es_correcta,
        'mensaje': '✅ ¡Correcto!' if es_correcta else '❌ No es correcto. Sigue practicando.',
        'respuesta_correcta': pregunta.respuesta_correcta,
        'puntos_obtenidos': respuesta_obj.puntos_obtenidos,
        'puntos_totales': pregunta.puntos,
    })

@staff_member_required
def importar_preguntas_json(request):
    """Importar preguntas desde archivo JSON"""
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        try:
            datos = json.load(archivo)
            preguntas = datos.get('preguntas', [])
            
            importadas = 0
            for p in preguntas:
                PreguntaGenerada.objects.create(
                    tipo=p.get('tipo', 'desarrollo'),
                    titulo=p.get('titulo', 'Sin título'),
                    enunciado=p.get('enunciado', ''),
                    respuesta_correcta=p.get('respuesta_correcta', ''),
                    pista=p.get('pista', ''),
                    dificultad=p.get('dificultad', 1),
                    puntos=p.get('puntos', 10),
                    categoria=p.get('categoria', ''),
                    ejercicio_base_id=p.get('ejercicio_base_id'),
                    creado_por=request.user,
                    activa=True,
                )
                importadas += 1
            
            return JsonResponse({
                'success': True,
                'importadas': importadas,
                'mensaje': f'✅ {importadas} preguntas importadas'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return render(request, 'core/preguntas/importar.html')

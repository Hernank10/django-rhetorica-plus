"""Vistas completas para cursos, lecciones y evaluaciones"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models_cursos import Curso, Modulo, Leccion, EvaluacionCurso, PreguntaEvaluacion

@login_required
def lista_cursos(request):
    cursos = Curso.objects.filter(estado='publicado')
    context = {
        'cursos': cursos,
        'total_cursos': cursos.count(),
    }
    return render(request, 'core/cursos/lista.html', context)

@login_required
def detalle_curso(request, curso_slug):
    """Mostrar detalle de un curso con módulos y lecciones"""
    try:
        curso = Curso.objects.get(slug=curso_slug)
    except Curso.DoesNotExist:
        messages.error(request, 'Curso no encontrado')
        return redirect('lista_cursos')
    
    # Obtener módulos con lecciones
    modulos = curso.modulos.all().order_by('orden')
    modulos_data = []
    for modulo in modulos:
        lecciones = modulo.lecciones.all().order_by('orden')
        modulos_data.append({
            'modulo': modulo,
            'lecciones': lecciones,
            'progreso': 0,
        })
    
    # Obtener evaluaciones del curso
    evaluaciones = EvaluacionCurso.objects.filter(curso=curso)
    
    context = {
        'curso': curso,
        'modulos': modulos_data,
        'evaluaciones': evaluaciones,
        'progreso_total': 0,
    }
    return render(request, 'core/cursos/detalle_completo.html', context)

@login_required
def ver_leccion(request, curso_slug, modulo_id, leccion_id):
    """Ver una lección específica"""
    curso = get_object_or_404(Curso, slug=curso_slug)
    modulo = get_object_or_404(Modulo, id=modulo_id, curso=curso)
    leccion = get_object_or_404(Leccion, id=leccion_id, modulo=modulo)
    
    ejercicios = leccion.ejercicios_relacionados.all()
    evaluaciones = EvaluacionCurso.objects.filter(modulo=modulo)
    
    lecciones = list(modulo.lecciones.all().order_by('orden'))
    idx = lecciones.index(leccion)
    leccion_anterior = lecciones[idx - 1] if idx > 0 else None
    leccion_siguiente = lecciones[idx + 1] if idx < len(lecciones) - 1 else None
    
    context = {
        'curso': curso,
        'modulo': modulo,
        'leccion': leccion,
        'ejercicios': ejercicios,
        'evaluaciones': evaluaciones,
        'leccion_anterior': leccion_anterior,
        'leccion_siguiente': leccion_siguiente,
    }
    return render(request, 'core/cursos/leccion_detalle.html', context)

@login_required
def ver_evaluacion(request, evaluacion_id):
    """Ver una evaluación para realizar"""
    evaluacion = get_object_or_404(EvaluacionCurso, id=evaluacion_id)
    preguntas = PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).order_by('orden')
    
    curso = evaluacion.curso
    modulo = evaluacion.modulo
    
    context = {
        'evaluacion': evaluacion,
        'preguntas': preguntas,
        'curso': curso,
        'modulo': modulo,
        'leccion': None,
        'total_preguntas': preguntas.count(),
        'intento_actual': 1,
    }
    return render(request, 'core/cursos/evaluacion_detalle.html', context)

@login_required
def enviar_evaluacion(request, evaluacion_id):
    """Procesar el envío de una evaluación"""
    if request.method != 'POST':
        return redirect('lista_cursos')
    
    evaluacion = get_object_or_404(EvaluacionCurso, id=evaluacion_id)
    preguntas = PreguntaEvaluacion.objects.filter(evaluacion=evaluacion)
    
    puntaje_obtenido = 0
    respuestas = {}
    
    for pregunta in preguntas:
        respuesta_usuario = request.POST.get(f'pregunta_{pregunta.id}', '').strip()
        respuestas[str(pregunta.id)] = respuesta_usuario
        
        if respuesta_usuario.lower() == pregunta.respuesta_correcta.lower():
            puntaje_obtenido += pregunta.puntaje
    
    messages.success(request, f'✅ Evaluación completada! Puntaje: {puntaje_obtenido}/{evaluacion.puntaje_maximo}')
    return redirect('detalle_curso', curso_slug=evaluacion.curso.slug)

@login_required
def resultado_evaluacion(request, evaluacion_id):
    """Ver resultado de una evaluación"""
    evaluacion = get_object_or_404(EvaluacionCurso, id=evaluacion_id)
    
    context = {
        'evaluacion': evaluacion,
        'preguntas': PreguntaEvaluacion.objects.filter(evaluacion=evaluacion),
    }
    return render(request, 'core/cursos/resultado_evaluacion.html', context)

def api_evaluacion_preguntas(request, evaluacion_id):
    """API para obtener preguntas de una evaluación"""
    try:
        evaluacion = EvaluacionCurso.objects.get(id=evaluacion_id)
        preguntas = PreguntaEvaluacion.objects.filter(evaluacion=evaluacion).order_by('orden')
        
        data = []
        for p in preguntas:
            data.append({
                'id': p.id,
                'enunciado': p.enunciado,
                'tipo': p.tipo,
                'opciones': p.opciones if p.opciones else [],
                'puntaje': p.puntaje,
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def detalle_curso(request, curso_slug):
    """Mostrar detalle de un curso con módulos y lecciones"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"=== DETALLE CURSO: {curso_slug} ===")
    print(f"=== DETALLE CURSO: {curso_slug} ===")
    
    try:
        curso = Curso.objects.get(slug=curso_slug)
        print(f"✅ Curso encontrado: {curso.titulo} (ID: {curso.id})")
        logger.info(f"Curso encontrado: {curso.titulo}")
    except Curso.DoesNotExist:
        print(f"❌ Curso NO encontrado con slug: {curso_slug}")
        messages.error(request, 'Curso no encontrado')
        return redirect('lista_cursos')
    
    # Obtener módulos con lecciones
    modulos = curso.modulos.all().order_by('orden')
    modulos_data = []
    for modulo in modulos:
        lecciones = modulo.lecciones.all().order_by('orden')
        print(f"  📂 Módulo: {modulo.titulo} - {lecciones.count()} lecciones")
        modulos_data.append({
            'modulo': modulo,
            'lecciones': lecciones,
            'progreso': 0,
        })
    
    # Obtener evaluaciones del curso
    evaluaciones = EvaluacionCurso.objects.filter(curso=curso)
    print(f"  📝 Evaluaciones: {evaluaciones.count()}")
    
    context = {
        'curso': curso,
        'modulos': modulos_data,
        'evaluaciones': evaluaciones,
        'progreso_total': 0,
    }
    return render(request, 'core/cursos/detalle_completo.html', context)

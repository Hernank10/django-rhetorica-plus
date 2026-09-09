"""Vistas para el sistema de cursos"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

# Importar modelos de cursos (si existen, si no, crear modelos básicos)
try:
    from .models_cursos import Curso, Modulo, Leccion, ProgresoUsuario
except ImportError:
    # Si no existen los modelos, crear modelos temporales
    from django.db import models
    
    class Curso:
        pass
    class Modulo:
        pass
    class Leccion:
        pass
    class ProgresoUsuario:
        pass

@login_required
def lista_cursos(request):
    """Mostrar todos los cursos disponibles"""
    
    # Intentar obtener cursos de la base de datos
    try:
        from .models_cursos import Curso
        cursos = Curso.objects.filter(estado='publicado')
        
        # Obtener progreso del usuario para cada curso
        for curso in cursos:
            curso.progreso_usuario = curso.get_progreso_usuario(request.user)
    except:
        # Si no hay modelo de cursos, mostrar mensaje
        cursos = []
        messages.info(request, '📚 Los cursos se están generando...')
    
    context = {
        'cursos': cursos,
        'total_cursos': len(cursos),
    }
    return render(request, 'core/cursos/lista.html', context)

@login_required
def detalle_curso(request, curso_slug):
    """Mostrar detalle de un curso con sus módulos y lecciones"""
    
    try:
        from .models_cursos import Curso
        curso = get_object_or_404(Curso, slug=curso_slug, estado='publicado')
        
        # Obtener progreso del usuario
        progreso_general = curso.get_progreso_usuario(request.user)
        
        # Progreso por módulo
        modulos_con_progreso = []
        for modulo in curso.modulos.all():
            modulos_con_progreso.append({
                'modulo': modulo,
                'progreso': modulo.get_progreso_usuario(request.user),
                'lecciones': modulo.lecciones.all()
            })
        
        # Lecciones completadas del usuario
        from .models_cursos import ProgresoUsuario
        lecciones_completadas = ProgresoUsuario.objects.filter(
            usuario=request.user,
            completado=True
        ).values_list('leccion_id', flat=True)
        
        context = {
            'curso': curso,
            'progreso_general': progreso_general,
            'modulos': modulos_con_progreso,
            'usuario_lecciones_completadas': lecciones_completadas,
        }
    except:
        messages.warning(request, '⚠️ El curso no está disponible temporalmente')
        return redirect('lista_cursos')
    
    return render(request, 'core/cursos/detalle.html', context)

@login_required
def ver_leccion(request, curso_slug, modulo_id, leccion_id):
    """Ver una lección específica"""
    
    try:
        from .models_cursos import Curso, Modulo, Leccion, ProgresoUsuario
        
        curso = get_object_or_404(Curso, slug=curso_slug)
        modulo = get_object_or_404(Modulo, id=modulo_id, curso=curso)
        leccion = get_object_or_404(Leccion, id=leccion_id, modulo=modulo)
        
        # Obtener o crear progreso
        progreso, created = ProgresoUsuario.objects.get_or_create(
            usuario=request.user,
            leccion=leccion
        )
        
        # Lección siguiente y anterior
        lecciones = list(modulo.lecciones.all().order_by('orden'))
        idx = lecciones.index(leccion)
        leccion_anterior = lecciones[idx - 1] if idx > 0 else None
        leccion_siguiente = lecciones[idx + 1] if idx < len(lecciones) - 1 else None
        
        context = {
            'curso': curso,
            'modulo': modulo,
            'leccion': leccion,
            'progreso': progreso,
            'leccion_anterior': leccion_anterior,
            'leccion_siguiente': leccion_siguiente,
            'ejercicios': leccion.ejercicios_relacionados.all(),
            'tecnicas': leccion.tecnicas_relacionadas.all(),
        }
    except:
        messages.warning(request, '⚠️ La lección no está disponible')
        return redirect('lista_cursos')
    
    return render(request, 'core/cursos/leccion.html', context)

@login_required
def marcar_leccion_completa(request, leccion_id):
    """Marcar una lección como completada"""
    
    if request.method != 'POST':
        return redirect('lista_cursos')
    
    try:
        from .models_cursos import Leccion, ProgresoUsuario
        
        leccion = get_object_or_404(Leccion, id=leccion_id)
        progreso, created = ProgresoUsuario.objects.get_or_create(
            usuario=request.user,
            leccion=leccion
        )
        progreso.marcar_completado()
        messages.success(request, f'✅ Lección "{leccion.titulo}" completada!')
    except:
        messages.warning(request, '⚠️ Error al marcar la lección')
    
    return redirect('lista_cursos')

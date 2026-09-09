from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg, Max, Min
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
import json
import os

from .models import (
    User, Respuesta, ProgresoCategoria, 
    EjercicioLinguistico, TecnicaLinguistica, ContenidoJSON, 
    Evaluacion, ResultadoEvaluacion, Logro, LogroObtenido,
    Certificacion, CertificacionObtenida
)

# ==================== VISTAS PÚBLICAS ====================

def index(request):
    """Vista principal de la plataforma"""
    total_ejercicios = EjercicioLinguistico.objects.count()
    total_tecnicas = TecnicaLinguistica.objects.count()
    total_contenidos = ContenidoJSON.objects.count()
    
    context = {
        'total_ejercicios': total_ejercicios,
        'total_tecnicas': total_tecnicas,
        'total_contenidos': total_contenidos,
        'ejercicios_recientes': EjercicioLinguistico.objects.all().order_by('-creado_en')[:5],
    }
    return render(request, 'core/index.html', context)

# ==================== API ENDPOINTS ====================

def ejercicios_json(request):
    """API para obtener ejercicios en JSON"""
    ejercicios = EjercicioLinguistico.objects.all().values(
        'id', 'titulo', 'categoria', 'tipo', 'nivel', 'puntos', 'contenido'
    )
    return JsonResponse(list(ejercicios), safe=False)

def tecnicas_json(request):
    """API para obtener técnicas en JSON"""
    tecnicas = TecnicaLinguistica.objects.all().values(
        'id', 'nombre', 'categoria', 'descripcion'
    )
    return JsonResponse(list(tecnicas), safe=False)

def contenidos_json(request):
    """API para obtener todos los contenidos JSON"""
    contenidos = ContenidoJSON.objects.all().values(
        'id', 'nombre', 'categoria', 'datos'
    )
    return JsonResponse(list(contenidos), safe=False)

def evaluaciones_json(request):
    """API para obtener evaluaciones disponibles"""
    evaluaciones = Evaluacion.objects.filter(activa=True).values(
        'id', 'titulo', 'descripcion', 'tipo', 'categoria',
        'puntos_base', 'duracion_minutos', 'nivel_requerido', 'preguntas'
    )
    return JsonResponse(list(evaluaciones), safe=False)

# ==================== DASHBOARD DEL ESTUDIANTE (CORREGIDO) ====================

@login_required
def dashboard_estudiante(request):
    """Dashboard principal del estudiante con progreso y actividades"""
    # Obtener el usuario actual correctamente
    user = request.user
    
    # Verificar que user es una instancia de User
    if not isinstance(user, User):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
            return redirect('core:index')
    
    total_ejercicios = EjercicioLinguistico.objects.count()
    
    # Obtener ejercicios completados por el usuario
    ejercicios_completados = Respuesta.objects.filter(user=user).values('item_id').distinct().count()
    
    # Progreso por categorías
    categorias = EjercicioLinguistico.objects.values('categoria').annotate(
        total=Count('id')
    ).exclude(categoria__isnull=True)
    
    categorias_progreso = []
    for cat in categorias:
        completados = Respuesta.objects.filter(
            user=user, 
            tipo_ejercicio=cat['categoria'],
            es_correcta=True
        ).values('item_id').distinct().count()
        
        porcentaje = int((completados / cat['total']) * 100) if cat['total'] > 0 else 0
        categorias_progreso.append({
            'nombre': cat['categoria'],
            'total': cat['total'],
            'completados': completados,
            'porcentaje': porcentaje,
            'nivel_dominio': 1 if porcentaje < 20 else 2 if porcentaje < 40 else 3 if porcentaje < 60 else 4 if porcentaje < 80 else 5
        })
    
    # Ejercicios recomendados (no completados)
    ejercicios_completados_ids = Respuesta.objects.filter(
        user=user
    ).values_list('item_id', flat=True)
    
    ejercicios_recomendados = EjercicioLinguistico.objects.exclude(
        id__in=ejercicios_completados_ids
    ).order_by('?')[:6]
    
    # Calcular racha
    racha = 0
    if user.ultima_actividad:
        dias_diferencia = (timezone.now().date() - user.ultima_actividad.date()).days
        if dias_diferencia <= 1:
            fechas_respuestas = Respuesta.objects.filter(
                user=user
            ).values_list('fecha__date', flat=True).distinct().order_by('-fecha__date')
            
            for i, fecha in enumerate(fechas_respuestas):
                if i == 0:
                    if fecha == timezone.now().date():
                        racha = 1
                    else:
                        break
                else:
                    if fecha == timezone.now().date() - timedelta(days=i):
                        racha += 1
                    else:
                        break
    
    consejos = [
        "La práctica constante es la clave para dominar cualquier disciplina lingüística.",
        "Lee en voz alta para mejorar tu pronunciación y comprensión.",
        "La escritura a mano ayuda a fijar mejor los conceptos.",
        "Cada error es una oportunidad para aprender algo nuevo.",
        "La retórica es el arte de la persuasión: practícala en tu vida diaria.",
        "La etimología te ayuda a comprender el origen y evolución de las palabras.",
        "La gramática es la columna vertebral de cualquier idioma.",
        "La lectura crítica desarrolla tu pensamiento analítico.",
        "La práctica de la escritura mejora tu capacidad de expresión.",
        "El aprendizaje de idiomas abre puertas a nuevas culturas."
    ]
    
    import random
    consejo_dia = random.choice(consejos)
    
    context = {
        'user': user,
        'total_ejercicios': total_ejercicios,
        'ejercicios_completados': ejercicios_completados,
        'ejercicios_recomendados': ejercicios_recomendados,
        'categorias_progreso': categorias_progreso[:8],
        'racha': racha,
        'consejo_dia': consejo_dia,
        'progreso_total': int((ejercicios_completados / total_ejercicios) * 100) if total_ejercicios > 0 else 0,
    }
    
    return render(request, 'core/dashboard_estudiante.html', context)

@login_required
def dashboard_gamificacion(request):
    """Dashboard de gamificación con logros, medallas y certificaciones"""
    user = request.user
    
    logros_disponibles = Logro.objects.all()
    logros_obtenidos = LogroObtenido.objects.filter(user=user)
    logros_obtenidos_ids = list(logros_obtenidos.values_list('logro_id', flat=True))
    
    total_ejercicios = EjercicioLinguistico.objects.count()
    total_completados = Respuesta.objects.filter(user=user).values('item_id').distinct().count()
    
    respuestas_correctas = Respuesta.objects.filter(user=user, es_correcta=True).count()
    respuestas_totales = Respuesta.objects.filter(user=user).count()
    tasa_aciertos = int((respuestas_correctas / respuestas_totales) * 100) if respuestas_totales > 0 else 0
    
    evaluaciones_disponibles = Evaluacion.objects.filter(
        activa=True,
        nivel_requerido__lte=user.nivel_experiencia
    )[:5]
    
    ejercicios_completados_ids = Respuesta.objects.filter(
        user=user
    ).values_list('item_id', flat=True)
    
    actividades_recomendadas = EjercicioLinguistico.objects.exclude(
        id__in=ejercicios_completados_ids
    ).order_by('?')[:5]
    
    ranking_estudiantes = User.objects.filter(
        is_staff=False
    ).order_by('-points')[:10]
    
    user_medallas = user.medallas if user.medallas else []
    user_certificaciones = user.certificaciones if user.certificaciones else []
    
    context = {
        'user': user,
        'logros_disponibles': logros_disponibles,
        'logros_obtenidos': logros_obtenidos,
        'logros_obtenidos_ids': logros_obtenidos_ids,
        'total_ejercicios': total_ejercicios,
        'total_completados': total_completados,
        'tasa_aciertos': tasa_aciertos,
        'evaluaciones_disponibles': evaluaciones_disponibles,
        'actividades_recomendadas': actividades_recomendadas,
        'ranking_estudiantes': ranking_estudiantes,
        'user_medallas': user_medallas,
        'user_certificaciones': user_certificaciones,
    }
    
    return render(request, 'core/dashboard_gamificacion.html', context)

# ==================== DASHBOARD DEL PROFESOR ====================

@staff_member_required
def dashboard_profesor(request):
    """Dashboard principal del profesor con estadísticas y gestión"""
    total_ejercicios = EjercicioLinguistico.objects.count()
    total_tecnicas = TecnicaLinguistica.objects.count()
    total_contenidos = ContenidoJSON.objects.count()
    total_estudiantes = User.objects.filter(is_staff=False).count()
    total_evaluaciones = Evaluacion.objects.count()
    total_logros = Logro.objects.count()
    
    estudiantes_activos = User.objects.filter(
        is_staff=False,
        ultima_actividad__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    promedio_puntos = User.objects.filter(is_staff=False).aggregate(
        avg_points=Avg('points')
    )['avg_points'] or 0
    
    ejercicios_populares = EjercicioLinguistico.objects.annotate(
        total_respuestas=Count('respuesta')
    ).order_by('-total_respuestas')[:5]
    
    top_estudiantes = User.objects.filter(
        is_staff=False
    ).order_by('-points')[:5]
    
    evaluaciones_recientes = ResultadoEvaluacion.objects.filter(
        completada=True
    ).order_by('-fecha_completada')[:10]
    
    progreso_general = []
    for categoria in EjercicioLinguistico.objects.values('categoria').distinct():
        if categoria['categoria']:
            total = EjercicioLinguistico.objects.filter(categoria=categoria['categoria']).count()
            completados = Respuesta.objects.filter(
                tipo_ejercicio=categoria['categoria'],
                es_correcta=True
            ).values('user', 'item_id').distinct().count()
            
            progreso_general.append({
                'categoria': categoria['categoria'],
                'total': total,
                'completados': completados,
                'porcentaje': int((completados / (total * total_estudiantes)) * 100) if total_estudiantes > 0 else 0
            })
    
    context = {
        'total_ejercicios': total_ejercicios,
        'total_tecnicas': total_tecnicas,
        'total_contenidos': total_contenidos,
        'total_estudiantes': total_estudiantes,
        'total_evaluaciones': total_evaluaciones,
        'total_logros': total_logros,
        'estudiantes_activos': estudiantes_activos,
        'promedio_puntos': int(promedio_puntos),
        'ejercicios_populares': ejercicios_populares,
        'top_estudiantes': top_estudiantes,
        'evaluaciones_recientes': evaluaciones_recientes,
        'progreso_general': progreso_general[:8],
        'ejercicios_recientes': EjercicioLinguistico.objects.all().order_by('-creado_en')[:10],
        'contenidos_recientes': ContenidoJSON.objects.all().order_by('-creado_en')[:10],
        'fecha_actual': timezone.now(),
    }
    return render(request, 'core/dashboard_profesor.html', context)

# ==================== GESTIÓN DE EJERCICIOS (PROFESOR) ====================

@staff_member_required
def gestion_ejercicios(request):
    """Lista de ejercicios para gestionar"""
    ejercicios = EjercicioLinguistico.objects.all().order_by('-creado_en')
    categorias = EjercicioLinguistico.objects.values_list('categoria', flat=True).distinct()
    
    context = {
        'ejercicios': ejercicios,
        'categorias': categorias,
        'total': ejercicios.count(),
    }
    return render(request, 'core/profesor/gestion_ejercicios.html', context)

@staff_member_required
def crear_ejercicio(request):
    """Crear un nuevo ejercicio"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        categoria = request.POST.get('categoria')
        tipo = request.POST.get('tipo')
        nivel = int(request.POST.get('nivel', 1))
        puntos = int(request.POST.get('puntos', 10))
        contenido_json = request.POST.get('contenido_json', '{}')
        
        try:
            contenido = json.loads(contenido_json)
        except:
            contenido = {}
        
        ejercicio = EjercicioLinguistico.objects.create(
            titulo=titulo,
            categoria=categoria,
            tipo=tipo,
            nivel=nivel,
            puntos=puntos,
            contenido=contenido
        )
        
        messages.success(request, f'Ejercicio "{ejercicio.titulo}" creado exitosamente.')
        return redirect('core:gestion_ejercicios')
    
    context = {
        'categorias': EjercicioLinguistico.objects.values_list('categoria', flat=True).distinct(),
        'tipos': ['Gramática', 'Retórica', 'Sintaxis', 'Semántica', 'Fonética', 'Ortografía', 'Literatura', 'General'],
    }
    return render(request, 'core/profesor/crear_ejercicio.html', context)

@staff_member_required
def editar_ejercicio(request, ejercicio_id):
    """Editar un ejercicio existente"""
    ejercicio = get_object_or_404(EjercicioLinguistico, id=ejercicio_id)
    
    if request.method == 'POST':
        ejercicio.titulo = request.POST.get('titulo')
        ejercicio.categoria = request.POST.get('categoria')
        ejercicio.tipo = request.POST.get('tipo')
        ejercicio.nivel = int(request.POST.get('nivel', 1))
        ejercicio.puntos = int(request.POST.get('puntos', 10))
        
        contenido_json = request.POST.get('contenido_json', '{}')
        try:
            ejercicio.contenido = json.loads(contenido_json)
        except:
            ejercicio.contenido = {}
        
        ejercicio.save()
        messages.success(request, f'Ejercicio "{ejercicio.titulo}" actualizado exitosamente.')
        return redirect('core:gestion_ejercicios')
    
    context = {
        'ejercicio': ejercicio,
        'categorias': EjercicioLinguistico.objects.values_list('categoria', flat=True).distinct(),
        'tipos': ['Gramática', 'Retórica', 'Sintaxis', 'Semántica', 'Fonética', 'Ortografía', 'Literatura', 'General'],
        'contenido_json': json.dumps(ejercicio.contenido, ensure_ascii=False, indent=2)
    }
    return render(request, 'core/profesor/editar_ejercicio.html', context)

@staff_member_required
def eliminar_ejercicio(request, ejercicio_id):
    """Eliminar un ejercicio"""
    ejercicio = get_object_or_404(EjercicioLinguistico, id=ejercicio_id)
    
    if request.method == 'POST':
        titulo = ejercicio.titulo
        ejercicio.delete()
        messages.success(request, f'Ejercicio "{titulo}" eliminado exitosamente.')
        return redirect('core:gestion_ejercicios')
    
    context = {'ejercicio': ejercicio}
    return render(request, 'core/profesor/eliminar_ejercicio.html', context)

# ==================== GESTIÓN DE TÉCNICAS (PROFESOR) ====================

@staff_member_required
def gestion_tecnicas(request):
    """Lista de técnicas para gestionar"""
    tecnicas = TecnicaLinguistica.objects.all().order_by('-creado_en')
    categorias = TecnicaLinguistica.objects.values_list('categoria', flat=True).distinct()
    
    context = {
        'tecnicas': tecnicas,
        'categorias': categorias,
        'total': tecnicas.count(),
    }
    return render(request, 'core/profesor/gestion_tecnicas.html', context)

@staff_member_required
def crear_tecnica(request):
    """Crear una nueva técnica"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        categoria = request.POST.get('categoria')
        nivel = int(request.POST.get('nivel', 1))
        
        tecnica = TecnicaLinguistica.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            categoria=categoria,
            nivel=nivel
        )
        
        messages.success(request, f'Técnica "{tecnica.nombre}" creada exitosamente.')
        return redirect('core:gestion_tecnicas')
    
    context = {
        'categorias': TecnicaLinguistica.objects.values_list('categoria', flat=True).distinct(),
    }
    return render(request, 'core/profesor/crear_tecnica.html', context)

@staff_member_required
def editar_tecnica(request, tecnica_id):
    """Editar una técnica existente"""
    tecnica = get_object_or_404(TecnicaLinguistica, id=tecnica_id)
    
    if request.method == 'POST':
        tecnica.nombre = request.POST.get('nombre')
        tecnica.descripcion = request.POST.get('descripcion')
        tecnica.categoria = request.POST.get('categoria')
        tecnica.nivel = int(request.POST.get('nivel', 1))
        tecnica.save()
        
        messages.success(request, f'Técnica "{tecnica.nombre}" actualizada exitosamente.')
        return redirect('core:gestion_tecnicas')
    
    context = {
        'tecnica': tecnica,
        'categorias': TecnicaLinguistica.objects.values_list('categoria', flat=True).distinct(),
    }
    return render(request, 'core/profesor/editar_tecnica.html', context)

@staff_member_required
def eliminar_tecnica(request, tecnica_id):
    """Eliminar una técnica"""
    tecnica = get_object_or_404(TecnicaLinguistica, id=tecnica_id)
    
    if request.method == 'POST':
        nombre = tecnica.nombre
        tecnica.delete()
        messages.success(request, f'Técnica "{nombre}" eliminada exitosamente.')
        return redirect('core:gestion_tecnicas')
    
    context = {'tecnica': tecnica}
    return render(request, 'core/profesor/eliminar_tecnica.html', context)

# ==================== GESTIÓN DE CONTENIDOS JSON (PROFESOR) ====================

@staff_member_required
def gestion_contenidos(request):
    """Lista de contenidos JSON para gestionar"""
    contenidos = ContenidoJSON.objects.all().order_by('-creado_en')
    categorias = ContenidoJSON.objects.values_list('categoria', flat=True).distinct()
    
    context = {
        'contenidos': contenidos,
        'categorias': categorias,
        'total': contenidos.count(),
    }
    return render(request, 'core/profesor/gestion_contenidos.html', context)

@staff_member_required
def crear_contenido(request):
    """Crear un nuevo contenido JSON"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        archivo = request.POST.get('archivo')
        categoria = request.POST.get('categoria')
        datos_json = request.POST.get('datos_json', '{}')
        
        try:
            datos = json.loads(datos_json)
        except:
            datos = {}
        
        contenido = ContenidoJSON.objects.create(
            nombre=nombre,
            archivo=archivo,
            categoria=categoria,
            datos=datos
        )
        
        messages.success(request, f'Contenido "{contenido.nombre}" creado exitosamente.')
        return redirect('core:gestion_contenidos')
    
    context = {
        'categorias': ContenidoJSON.objects.values_list('categoria', flat=True).distinct(),
    }
    return render(request, 'core/profesor/crear_contenido.html', context)

@staff_member_required
def editar_contenido(request, contenido_id):
    """Editar un contenido JSON existente"""
    contenido = get_object_or_404(ContenidoJSON, id=contenido_id)
    
    if request.method == 'POST':
        contenido.nombre = request.POST.get('nombre')
        contenido.archivo = request.POST.get('archivo')
        contenido.categoria = request.POST.get('categoria')
        
        datos_json = request.POST.get('datos_json', '{}')
        try:
            contenido.datos = json.loads(datos_json)
        except:
            contenido.datos = {}
        
        contenido.save()
        messages.success(request, f'Contenido "{contenido.nombre}" actualizado exitosamente.')
        return redirect('core:gestion_contenidos')
    
    context = {
        'contenido': contenido,
        'categorias': ContenidoJSON.objects.values_list('categoria', flat=True).distinct(),
        'datos_json': json.dumps(contenido.datos, ensure_ascii=False, indent=2)
    }
    return render(request, 'core/profesor/editar_contenido.html', context)

@staff_member_required
def eliminar_contenido(request, contenido_id):
    """Eliminar un contenido JSON"""
    contenido = get_object_or_404(ContenidoJSON, id=contenido_id)
    
    if request.method == 'POST':
        nombre = contenido.nombre
        contenido.delete()
        messages.success(request, f'Contenido "{nombre}" eliminado exitosamente.')
        return redirect('core:gestion_contenidos')
    
    context = {'contenido': contenido}
    return render(request, 'core/profesor/eliminar_contenido.html', context)

# ==================== GESTIÓN DE ESTUDIANTES (PROFESOR) ====================

@staff_member_required
def gestion_estudiantes(request):
    """Lista de estudiantes con estadísticas"""
    estudiantes = User.objects.filter(is_staff=False).annotate(
        total_respuestas=Count('respuestas'),
        respuestas_correctas=Count('respuestas', filter=Q(respuestas__es_correcta=True))
    ).order_by('-points')
    
    context = {
        'estudiantes': estudiantes,
        'total': estudiantes.count(),
    }
    return render(request, 'core/profesor/gestion_estudiantes.html', context)

@staff_member_required
def detalle_estudiante(request, estudiante_id):
    """Ver detalles de un estudiante específico"""
    estudiante = get_object_or_404(User, id=estudiante_id, is_staff=False)
    
    respuestas = Respuesta.objects.filter(user=estudiante)
    total_respuestas = respuestas.count()
    respuestas_correctas = respuestas.filter(es_correcta=True).count()
    tasa_aciertos = int((respuestas_correctas / total_respuestas) * 100) if total_respuestas > 0 else 0
    
    progreso_categorias = ProgresoCategoria.objects.filter(user=estudiante)
    logros = LogroObtenido.objects.filter(user=estudiante).select_related('logro')
    evaluaciones = ResultadoEvaluacion.objects.filter(
        user=estudiante,
        completada=True
    ).select_related('evaluacion').order_by('-fecha_completada')
    actividad_reciente = respuestas.order_by('-fecha')[:20]
    
    context = {
        'estudiante': estudiante,
        'total_respuestas': total_respuestas,
        'respuestas_correctas': respuestas_correctas,
        'tasa_aciertos': tasa_aciertos,
        'progreso_categorias': progreso_categorias,
        'logros': logros,
        'evaluaciones': evaluaciones,
        'actividad_reciente': actividad_reciente,
    }
    return render(request, 'core/profesor/detalle_estudiante.html', context)

# ==================== AUTENTICACIÓN Y REGISTRO ====================

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def registro(request):
    """Vista de registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('core:dashboard_estudiante')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'core/registro.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return render(request, 'core/registro.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return render(request, 'core/registro.html')
        
        if len(password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'core/registro.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            user.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('core:dashboard_estudiante')
        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')
            return render(request, 'core/registro.html')
    
    return render(request, 'core/registro.html')

def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('core:dashboard_estudiante')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            user.ultima_actividad = timezone.now()
            user.save()
            messages.success(request, f'¡Bienvenido de vuelta {user.username}!')
            
            if user.is_staff:
                return redirect('core:dashboard_profesor')
            else:
                return redirect('core:dashboard_estudiante')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'core/login.html')
    
    return render(request, 'core/login.html')

def logout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('core:index')

# ==================== PERFIL DE USUARIO ====================

@login_required
def perfil_usuario(request):
    """Perfil completo del usuario con todas sus estadísticas"""
    user = request.user
    
    total_respuestas = Respuesta.objects.filter(user=user).count()
    respuestas_correctas = Respuesta.objects.filter(user=user, es_correcta=True).count()
    tasa_aciertos = int((respuestas_correctas / total_respuestas) * 100) if total_respuestas > 0 else 0
    
    tiempo_total = Respuesta.objects.filter(user=user).aggregate(
        total_tiempo=Sum('tiempo_segundos')
    )['total_tiempo'] or 0
    
    horas = tiempo_total // 3600
    minutos = (tiempo_total % 3600) // 60
    segundos = tiempo_total % 60
    
    progreso_categorias = ProgresoCategoria.objects.filter(user=user)
    logros_obtenidos = LogroObtenido.objects.filter(user=user).select_related('logro')
    
    fecha_limite = timezone.now() - timedelta(days=30)
    actividad_reciente = Respuesta.objects.filter(
        user=user,
        fecha__gte=fecha_limite
    ).order_by('-fecha')[:20]
    
    dias_activos = Respuesta.objects.filter(
        user=user
    ).values('fecha__date').distinct().count()
    
    evaluaciones_completadas = ResultadoEvaluacion.objects.filter(
        user=user,
        completada=True
    ).select_related('evaluacion')
    
    context = {
        'user': user,
        'total_respuestas': total_respuestas,
        'respuestas_correctas': respuestas_correctas,
        'tasa_aciertos': tasa_aciertos,
        'tiempo_total': tiempo_total,
        'horas': horas,
        'minutos': minutos,
        'segundos': segundos,
        'progreso_categorias': progreso_categorias,
        'logros_obtenidos': logros_obtenidos,
        'actividad_reciente': actividad_reciente,
        'dias_activos': dias_activos,
        'evaluaciones_completadas': evaluaciones_completadas,
        'medallas': user.medallas if user.medallas else [],
        'certificaciones': user.certificaciones if user.certificaciones else [],
        'nivel_experiencia': user.nivel_experiencia,
        'nivel': user.nivel,
    }
    return render(request, 'core/perfil_usuario.html', context)

@login_required
def editar_perfil(request):
    """Editar información del perfil"""
    user = request.user
    
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if email and email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'El correo electrónico ya está en uso.')
                return render(request, 'core/editar_perfil.html', {'user': user})
            user.email = email
        
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('core:perfil_usuario')
    
    return render(request, 'core/editar_perfil.html', {'user': user})

@login_required
def cambiar_contrasena(request):
    """Cambiar contraseña del usuario"""
    user = request.user
    
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual')
        password_nueva = request.POST.get('password_nueva')
        password_confirm = request.POST.get('password_confirm')
        
        if not user.check_password(password_actual):
            messages.error(request, 'La contraseña actual es incorrecta.')
            return render(request, 'core/cambiar_contrasena.html')
        
        if len(password_nueva) < 8:
            messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres.')
            return render(request, 'core/cambiar_contrasena.html')
        
        if password_nueva != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'core/cambiar_contrasena.html')
        
        user.set_password(password_nueva)
        user.save()
        login(request, user)
        
        messages.success(request, 'Contraseña cambiada exitosamente.')
        return redirect('core:perfil_usuario')
    
    return render(request, 'core/cambiar_contrasena.html')

def recuperar_contrasena(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            messages.success(request, f'Se ha enviado un enlace de recuperación a {email}')
            return redirect('core:login')
        except User.DoesNotExist:
            messages.error(request, 'No existe una cuenta con este correo electrónico.')
            return render(request, 'core/recuperar_contrasena.html')
    
    return render(request, 'core/recuperar_contrasena.html')

# ==================== API DE PERFIL ====================

@login_required
def api_perfil(request):
    """API para obtener datos del perfil en JSON"""
    user = request.user
    
    total_respuestas = Respuesta.objects.filter(user=user).count()
    respuestas_correctas = Respuesta.objects.filter(user=user, es_correcta=True).count()
    tasa_aciertos = int((respuestas_correctas / total_respuestas) * 100) if total_respuestas > 0 else 0
    
    return JsonResponse({
        'username': user.username,
        'email': user.email,
        'points': user.points,
        'nivel': user.nivel,
        'nivel_experiencia': user.nivel_experiencia,
        'estrellas': user.estrellas,
        'racha': user.racha,
        'total_respuestas': total_respuestas,
        'respuestas_correctas': respuestas_correctas,
        'tasa_aciertos': tasa_aciertos,
        'medallas': user.medallas if user.medallas else [],
        'certificaciones': user.certificaciones if user.certificaciones else [],
        'is_staff': user.is_staff,
        'date_joined': user.date_joined.strftime('%Y-%m-%d'),
        'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
    })

def verificar_usuario(request):
    """Verificar si el usuario está autenticado (API)"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'username': request.user.username,
            'email': request.user.email,
            'nivel': request.user.nivel,
            'points': request.user.points,
            'is_staff': request.user.is_staff,
        })
    return JsonResponse({'authenticated': False}, status=401)

# ==================== FUNCIONES AUXILIARES ====================

def verificar_logros(user):
    """Verifica y otorga logros automáticamente"""
    logros_disponibles = Logro.objects.all()
    
    for logro in logros_disponibles:
        if LogroObtenido.objects.filter(user=user, logro=logro).exists():
            continue
        
        cumple_requisitos = True
        
        if logro.puntos_requeridos > 0 and user.points < logro.puntos_requeridos:
            cumple_requisitos = False
        
        if logro.nivel_requerido > 0 and user.nivel_experiencia < logro.nivel_requerido:
            cumple_requisitos = False
        
        if logro.ejercicios_completados_requeridos > 0:
            completados = Respuesta.objects.filter(
                user=user, es_correcta=True
            ).values('item_id').distinct().count()
            if completados < logro.ejercicios_completados_requeridos:
                cumple_requisitos = False
        
        if cumple_requisitos:
            LogroObtenido.objects.create(user=user, logro=logro)
            
            if logro.tipo == 'medalla':
                if not user.medallas:
                    user.medallas = []
                user.medallas.append(logro.nombre)
            elif logro.tipo == 'certificacion':
                if not user.certificaciones:
                    user.certificaciones = []
                user.certificaciones.append(logro.nombre)
            elif logro.tipo == 'estrella':
                user.estrellas += 1
            
            user.save()

# ==================== GESTIÓN DE EVALUACIONES (PROFESOR) ====================

@staff_member_required
def gestion_evaluaciones(request):
    """Lista de evaluaciones para gestionar"""
    evaluaciones = Evaluacion.objects.all().order_by('-creada_en')
    
    context = {
        'evaluaciones': evaluaciones,
        'total': evaluaciones.count(),
    }
    return render(request, 'core/profesor/gestion_evaluaciones.html', context)

@staff_member_required
def crear_evaluacion(request):
    """Crear una nueva evaluación"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        tipo = request.POST.get('tipo')
        categoria = request.POST.get('categoria')
        nivel_requerido = int(request.POST.get('nivel_requerido', 1))
        puntos_base = int(request.POST.get('puntos_base', 10))
        duracion_minutos = int(request.POST.get('duracion_minutos', 30))
        preguntas_json = request.POST.get('preguntas_json', '[]')
        
        try:
            preguntas = json.loads(preguntas_json)
        except:
            preguntas = []
        
        evaluacion = Evaluacion.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            tipo=tipo,
            categoria=categoria,
            nivel_requerido=nivel_requerido,
            puntos_base=puntos_base,
            duracion_minutos=duracion_minutos,
            preguntas=preguntas,
            activa=True
        )
        
        messages.success(request, f'Evaluación "{evaluacion.titulo}" creada exitosamente.')
        return redirect('core:gestion_evaluaciones')
    
    context = {
        'tipos': ['diagnostico', 'formativa', 'sumativa', 'final'],
        'categorias': EjercicioLinguistico.objects.values_list('categoria', flat=True).distinct(),
    }
    return render(request, 'core/profesor/crear_evaluacion.html', context)

@staff_member_required
def editar_evaluacion(request, evaluacion_id):
    """Editar una evaluación existente"""
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)
    
    if request.method == 'POST':
        evaluacion.titulo = request.POST.get('titulo')
        evaluacion.descripcion = request.POST.get('descripcion')
        evaluacion.tipo = request.POST.get('tipo')
        evaluacion.categoria = request.POST.get('categoria')
        evaluacion.nivel_requerido = int(request.POST.get('nivel_requerido', 1))
        evaluacion.puntos_base = int(request.POST.get('puntos_base', 10))
        evaluacion.duracion_minutos = int(request.POST.get('duracion_minutos', 30))
        evaluacion.activa = request.POST.get('activa') == 'on'
        
        preguntas_json = request.POST.get('preguntas_json', '[]')
        try:
            evaluacion.preguntas = json.loads(preguntas_json)
        except:
            evaluacion.preguntas = []
        
        evaluacion.save()
        messages.success(request, f'Evaluación "{evaluacion.titulo}" actualizada exitosamente.')
        return redirect('core:gestion_evaluaciones')
    
    context = {
        'evaluacion': evaluacion,
        'tipos': ['diagnostico', 'formativa', 'sumativa', 'final'],
        'categorias': EjercicioLinguistico.objects.values_list('categoria', flat=True).distinct(),
        'preguntas_json': json.dumps(evaluacion.preguntas, ensure_ascii=False, indent=2)
    }
    return render(request, 'core/profesor/editar_evaluacion.html', context)

@staff_member_required
def eliminar_evaluacion(request, evaluacion_id):
    """Eliminar una evaluación"""
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)
    
    if request.method == 'POST':
        titulo = evaluacion.titulo
        evaluacion.delete()
        messages.success(request, f'Evaluación "{titulo}" eliminada exitosamente.')
        return redirect('core:gestion_evaluaciones')
    
    context = {'evaluacion': evaluacion}
    return render(request, 'core/profesor/eliminar_evaluacion.html', context)

# ==================== GESTIÓN DE LOGROS (PROFESOR) ====================

@staff_member_required
def gestion_logros(request):
    """Lista de logros para gestionar"""
    logros = Logro.objects.all().order_by('tipo', 'puntos_requeridos')
    
    context = {
        'logros': logros,
        'total': logros.count(),
    }
    return render(request, 'core/profesor/gestion_logros.html', context)

@staff_member_required
def crear_logro(request):
    """Crear un nuevo logro"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        tipo = request.POST.get('tipo')
        icono = request.POST.get('icono')
        color = request.POST.get('color')
        puntos_requeridos = int(request.POST.get('puntos_requeridos', 0))
        nivel_requerido = int(request.POST.get('nivel_requerido', 1))
        ejercicios_completados_requeridos = int(request.POST.get('ejercicios_completados_requeridos', 0))
        tasa_aciertos_requerida = float(request.POST.get('tasa_aciertos_requerida', 0))
        
        logro = Logro.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            tipo=tipo,
            icono=icono,
            color=color,
            puntos_requeridos=puntos_requeridos,
            nivel_requerido=nivel_requerido,
            ejercicios_completados_requeridos=ejercicios_completados_requeridos,
            tasa_aciertos_requerida=tasa_aciertos_requerida
        )
        
        messages.success(request, f'Logro "{logro.nombre}" creado exitosamente.')
        return redirect('core:gestion_logros')
    
    context = {
        'tipos': ['insignia', 'medalla', 'estrella', 'certificacion'],
        'colores': ['gold', 'silver', 'bronze', 'red', 'blue', 'green', 'purple', 'orange'],
    }
    return render(request, 'core/profesor/crear_logro.html', context)

@staff_member_required
def editar_logro(request, logro_id):
    """Editar un logro existente"""
    logro = get_object_or_404(Logro, id=logro_id)
    
    if request.method == 'POST':
        logro.nombre = request.POST.get('nombre')
        logro.descripcion = request.POST.get('descripcion')
        logro.tipo = request.POST.get('tipo')
        logro.icono = request.POST.get('icono')
        logro.color = request.POST.get('color')
        logro.puntos_requeridos = int(request.POST.get('puntos_requeridos', 0))
        logro.nivel_requerido = int(request.POST.get('nivel_requerido', 1))
        logro.ejercicios_completados_requeridos = int(request.POST.get('ejercicios_completados_requeridos', 0))
        logro.tasa_aciertos_requerida = float(request.POST.get('tasa_aciertos_requerida', 0))
        logro.save()
        
        messages.success(request, f'Logro "{logro.nombre}" actualizado exitosamente.')
        return redirect('core:gestion_logros')
    
    context = {
        'logro': logro,
        'tipos': ['insignia', 'medalla', 'estrella', 'certificacion'],
        'colores': ['gold', 'silver', 'bronze', 'red', 'blue', 'green', 'purple', 'orange'],
    }
    return render(request, 'core/profesor/editar_logro.html', context)

@staff_member_required
def eliminar_logro(request, logro_id):
    """Eliminar un logro"""
    logro = get_object_or_404(Logro, id=logro_id)
    
    if request.method == 'POST':
        nombre = logro.nombre
        logro.delete()
        messages.success(request, f'Logro "{nombre}" eliminado exitosamente.')
        return redirect('core:gestion_logros')
    
    context = {'logro': logro}
    return render(request, 'core/profesor/eliminar_logro.html', context)

# ==================== CARGA MASIVA Y EXPORTACIÓN ====================

@staff_member_required
def carga_masiva(request):
    """Carga masiva de datos desde archivos JSON"""
    if request.method == 'POST':
        carpeta = 'data'
        contador = 0
        errores = []
        
        for archivo in os.listdir(carpeta):
            if archivo.endswith('.json'):
                ruta = os.path.join(carpeta, archivo)
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    
                    categoria = archivo.replace('.json', '').replace('_', ' ').title()
                    
                    if isinstance(datos, list):
                        for item in datos:
                            titulo = item.get('titulo', item.get('nombre', 'Sin título'))
                            tipo = item.get('tipo', item.get('categoria', 'General'))
                            
                            EjercicioLinguistico.objects.create(
                                titulo=str(titulo)[:400],
                                contenido=item,
                                categoria=categoria,
                                tipo=str(tipo),
                                nivel=1,
                                puntos=10,
                                archivo_origen=archivo
                            )
                            contador += 1
                    elif isinstance(datos, dict):
                        EjercicioLinguistico.objects.create(
                            titulo=categoria[:400],
                            contenido=datos,
                            categoria=categoria,
                            archivo_origen=archivo,
                            nivel=1,
                            puntos=10
                        )
                        contador += 1
                        
                except Exception as e:
                    errores.append(f"{archivo}: {str(e)}")
        
        messages.success(request, f'Carga completada: {contador} ejercicios creados.')
        if errores:
            messages.warning(request, f'Errores en {len(errores)} archivos.')
        
        return redirect('core:dashboard_profesor')
    
    return render(request, 'core/profesor/carga_masiva.html')

@staff_member_required
def exportar_ejercicios(request):
    """Exportar todos los ejercicios en formato JSON"""
    ejercicios = EjercicioLinguistico.objects.all().values(
        'id', 'titulo', 'categoria', 'tipo', 'nivel', 'puntos', 'contenido', 'creado_en'
    )
    
    data = list(ejercicios)
    response = JsonResponse(data, safe=False)
    response['Content-Disposition'] = 'attachment; filename="ejercicios_exportados.json"'
    return response

@staff_member_required
def exportar_tecnicas(request):
    """Exportar todas las técnicas en formato JSON"""
    tecnicas = TecnicaLinguistica.objects.all().values(
        'id', 'nombre', 'descripcion', 'categoria', 'nivel', 'creado_en'
    )
    
    data = list(tecnicas)
    response = JsonResponse(data, safe=False)
    response['Content-Disposition'] = 'attachment; filename="tecnicas_exportadas.json"'
    return response

@staff_member_required
def exportar_contenidos(request):
    """Exportar todos los contenidos en formato JSON"""
    contenidos = ContenidoJSON.objects.all().values(
        'id', 'nombre', 'archivo', 'categoria', 'datos', 'creado_en'
    )
    
    data = list(contenidos)
    response = JsonResponse(data, safe=False)
    response['Content-Disposition'] = 'attachment; filename="contenidos_exportados.json"'
    return response

@staff_member_required
def estadisticas_contenido(request):
    """Estadísticas detalladas del contenido"""
    total_ejercicios = EjercicioLinguistico.objects.count()
    total_tecnicas = TecnicaLinguistica.objects.count()
    total_contenidos = ContenidoJSON.objects.count()
    
    ejercicios_por_categoria = EjercicioLinguistico.objects.values('categoria').annotate(
        total=Count('id'),
        nivel_promedio=Avg('nivel'),
        puntos_promedio=Avg('puntos')
    ).order_by('-total')
    
    tecnicas_por_categoria = TecnicaLinguistica.objects.values('categoria').annotate(
        total=Count('id')
    ).order_by('-total')
    
    ejercicios_por_nivel = EjercicioLinguistico.objects.values('nivel').annotate(
        total=Count('id')
    ).order_by('nivel')
    
    contenidos_por_categoria = ContenidoJSON.objects.values('categoria').annotate(
        total=Count('id')
    ).order_by('-total')
    
    ejercicios_populares = EjercicioLinguistico.objects.annotate(
        total_respuestas=Count('respuesta'),
        respuestas_correctas=Count('respuesta', filter=Q(respuesta__es_correcta=True))
    ).order_by('-total_respuestas')[:10]
    
    context = {
        'total_ejercicios': total_ejercicios,
        'total_tecnicas': total_tecnicas,
        'total_contenidos': total_contenidos,
        'ejercicios_por_categoria': ejercicios_por_categoria,
        'tecnicas_por_categoria': tecnicas_por_categoria,
        'ejercicios_por_nivel': ejercicios_por_nivel,
        'contenidos_por_categoria': contenidos_por_categoria,
        'ejercicios_populares': ejercicios_populares,
    }
    return render(request, 'core/profesor/estadisticas_contenido.html', context)

# ==================== VISUALIZACIÓN PÚBLICA ====================

def ver_contenido(request, contenido_id):
    """Ver un contenido JSON específico"""
    contenido = get_object_or_404(ContenidoJSON, id=contenido_id)
    
    context = {
        'contenido': contenido,
        'datos_formateados': json.dumps(contenido.datos, ensure_ascii=False, indent=2)
    }
    return render(request, 'core/ver_contenido.html', context)

def ver_tecnica(request, tecnica_id):
    """Ver una técnica específica"""
    tecnica = get_object_or_404(TecnicaLinguistica, id=tecnica_id)
    
    context = {
        'tecnica': tecnica,
        'ejercicios_relacionados': EjercicioLinguistico.objects.filter(
            categoria=tecnica.categoria
        )[:5]
    }
    return render(request, 'core/ver_tecnica.html', context)

def detalle_ejercicio(request, ejercicio_id):
    """Ver detalle de un ejercicio"""
    ejercicio = get_object_or_404(EjercicioLinguistico, id=ejercicio_id)
    
    relacionados = EjercicioLinguistico.objects.filter(
        categoria=ejercicio.categoria
    ).exclude(id=ejercicio.id)[:5]
    
    total_respuestas = Respuesta.objects.filter(item_id=ejercicio.id).count()
    respuestas_correctas = Respuesta.objects.filter(
        item_id=ejercicio.id,
        es_correcta=True
    ).count()
    tasa_aciertos = int((respuestas_correctas / total_respuestas) * 100) if total_respuestas > 0 else 0
    
    context = {
        'ejercicio': ejercicio,
        'relacionados': relacionados,
        'total_respuestas': total_respuestas,
        'respuestas_correctas': respuestas_correctas,
        'tasa_aciertos': tasa_aciertos,
        'contenido_formateado': json.dumps(ejercicio.contenido, ensure_ascii=False, indent=2)
    }
    return render(request, 'core/detalle_ejercicio.html', context)

# ==================== BÚSQUEDA ====================

def buscar_ejercicios(request):
    """Buscar ejercicios por título, categoría o tipo"""
    query = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    tipo = request.GET.get('tipo', '')
    nivel = request.GET.get('nivel', '')
    
    ejercicios = EjercicioLinguistico.objects.all()
    
    if query:
        ejercicios = ejercicios.filter(
            Q(titulo__icontains=query) |
            Q(categoria__icontains=query) |
            Q(tipo__icontains=query)
        )
    
    if categoria:
        ejercicios = ejercicios.filter(categoria=categoria)
    
    if tipo:
        ejercicios = ejercicios.filter(tipo=tipo)
    
    if nivel:
        ejercicios = ejercicios.filter(nivel=int(nivel))
    
    ejercicios = ejercicios.order_by('-creado_en')[:50]
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = list(ejercicios.values('id', 'titulo', 'categoria', 'tipo', 'nivel', 'puntos'))
        return JsonResponse(data, safe=False)
    
    context = {
        'ejercicios': ejercicios,
        'query': query,
        'categoria_seleccionada': categoria,
        'tipo_seleccionado': tipo,
        'nivel_seleccionado': nivel,
        'categorias': EjercicioLinguistico.objects.values_list('categoria', flat=True).distinct(),
        'tipos': EjercicioLinguistico.objects.values_list('tipo', flat=True).distinct(),
        'niveles': range(1, 6),
    }
    return render(request, 'core/buscar_ejercicios.html', context)

def buscar_tecnicas(request):
    """Buscar técnicas por nombre o categoría"""
    query = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    
    tecnicas = TecnicaLinguistica.objects.all()
    
    if query:
        tecnicas = tecnicas.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__icontains=query)
        )
    
    if categoria:
        tecnicas = tecnicas.filter(categoria=categoria)
    
    tecnicas = tecnicas.order_by('-creado_en')[:50]
    
    context = {
        'tecnicas': tecnicas,
        'query': query,
        'categoria_seleccionada': categoria,
        'categorias': TecnicaLinguistica.objects.values_list('categoria', flat=True).distinct(),
    }
    return render(request, 'core/buscar_tecnicas.html', context)

# ==================== ADMINISTRACIÓN DE USUARIOS ====================

@staff_member_required
def lista_usuarios(request):
    """Lista de todos los usuarios (solo para staff)"""
    usuarios = User.objects.all().annotate(
        total_respuestas=Count('respuestas'),
        respuestas_correctas=Count('respuestas', filter=Q(respuestas__es_correcta=True))
    ).order_by('-date_joined')
    
    context = {
        'usuarios': usuarios,
        'total': usuarios.count(),
        'usuarios_activos': usuarios.filter(is_active=True).count(),
        'usuarios_staff': usuarios.filter(is_staff=True).count(),
    }
    return render(request, 'core/lista_usuarios.html', context)

@staff_member_required
def toggle_usuario_activo(request, usuario_id):
    """Activar/desactivar un usuario (solo para staff)"""
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=usuario_id)
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        estado = 'activado' if usuario.is_active else 'desactivado'
        messages.success(request, f'Usuario {usuario.username} {estado} exitosamente.')
        return redirect('core:lista_usuarios')
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# ==================== PRÁCTICA DE EJERCICIOS ====================

@login_required
def practicar_ejercicio(request, ejercicio_id):
    """Vista para practicar un ejercicio específico"""
    ejercicio = get_object_or_404(EjercicioLinguistico, id=ejercicio_id)
    
    if request.method == 'POST':
        respuesta_usuario = request.POST.get('respuesta', '')
        tiempo = int(request.POST.get('tiempo', 0))
        
        es_correcta = False
        feedback = "Respuesta procesada. ¡Sigue practicando!"
        puntos_ganados = 0
        
        # Verificar si hay una respuesta correcta en el contenido
        if ejercicio.contenido and isinstance(ejercicio.contenido, dict):
            if 'respuesta_correcta' in ejercicio.contenido:
                if respuesta_usuario.lower().strip() == str(ejercicio.contenido['respuesta_correcta']).lower().strip():
                    es_correcta = True
                    puntos_ganados = ejercicio.puntos or 10
                    feedback = "¡Excelente! Respuesta correcta."
        
        # Guardar respuesta
        respuesta = Respuesta.objects.create(
            user=request.user,
            tipo_ejercicio=ejercicio.categoria or 'General',
            item_id=ejercicio.id,
            respuesta_usuario=respuesta_usuario,
            es_correcta=es_correcta,
            puntuacion=puntos_ganados,
            tiempo_segundos=tiempo,
            feedback=feedback
        )
        
        if es_correcta:
            request.user.points += puntos_ganados
            request.user.total_ejercicios_completados += 1
            request.user.ultima_actividad = timezone.now()
            request.user.save()
            
            # Actualizar progreso por categoría
            progreso, created = ProgresoCategoria.objects.get_or_create(
                user=request.user,
                categoria=ejercicio.categoria or 'General'
            )
            progreso.aciertos += 1
            progreso.intentos += 1
            progreso.save()
            
            # Verificar logros
            verificar_logros(request.user)
        
        return JsonResponse({
            'correcta': es_correcta,
            'puntos': puntos_ganados,
            'feedback': feedback,
            'total_puntos': request.user.points,
            'mensaje': '¡Respuesta correcta!' if es_correcta else 'Respuesta incorrecta. Sigue practicando.'
        })
    
    context = {
        'ejercicio': ejercicio,
    }
    return render(request, 'core/practicar_ejercicio.html', context)

# ==================== EVALUACIONES ====================

@login_required
def evaluacion_detalle(request, evaluacion_id):
    """Ver detalle de una evaluación"""
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id, activa=True)
    
    resultado_existente = ResultadoEvaluacion.objects.filter(
        user=request.user,
        evaluacion=evaluacion,
        completada=True
    ).first()
    
    if resultado_existente:
        messages.warning(request, 'Ya has completado esta evaluación.')
        return redirect('core:dashboard_estudiante')
    
    context = {
        'evaluacion': evaluacion,
    }
    return render(request, 'core/evaluacion_detalle.html', context)

@login_required
def enviar_evaluacion(request, evaluacion_id):
    """Enviar respuestas de una evaluación"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id, activa=True)
    
    respuestas = []
    puntaje_total = 0
    preguntas = evaluacion.preguntas
    
    for i, pregunta in enumerate(preguntas):
        respuesta_key = f'pregunta_{i}'
        respuesta_usuario = request.POST.get(respuesta_key, '')
        
        es_correcta = False
        if 'respuesta_correcta' in pregunta:
            if respuesta_usuario == pregunta['respuesta_correcta']:
                es_correcta = True
                puntaje_total += 1
        
        respuestas.append({
            'pregunta': pregunta.get('texto', ''),
            'respuesta': respuesta_usuario,
            'correcta': es_correcta
        })
    
    puntaje_porcentaje = int((puntaje_total / len(preguntas)) * 100) if preguntas else 0
    puntos_ganados = int((puntaje_porcentaje / 100) * evaluacion.puntos_base)
    
    calificacion = 'Excelente' if puntaje_porcentaje >= 90 else 'Bueno' if puntaje_porcentaje >= 75 else 'Regular' if puntaje_porcentaje >= 60 else 'Necesita Mejorar'
    
    resultado = ResultadoEvaluacion.objects.create(
        user=request.user,
        evaluacion=evaluacion,
        puntaje=puntaje_porcentaje,
        respuestas=respuestas,
        tiempo_utilizado=int(request.POST.get('tiempo', 0)),
        completada=True,
        fecha_completada=timezone.now(),
        calificacion=calificacion,
        feedback_general=f"Evaluación completada con {puntaje_porcentaje}% de aciertos."
    )
    
    request.user.points += puntos_ganados
    request.user.ultima_actividad = timezone.now()
    request.user.save()
    
    verificar_logros(request.user)
    
    return JsonResponse({
        'puntaje': puntaje_porcentaje,
        'puntos_ganados': puntos_ganados,
        'calificacion': calificacion,
        'total_puntos': request.user.points,
        'mensaje': f'¡Evaluación completada! Obtuviste {puntaje_porcentaje}% de aciertos.'
    })

# ==================== CERTIFICACIONES ====================

@login_required
def certificaciones_lista(request):
    """Lista de certificaciones disponibles y obtenidas"""
    user = request.user
    
    certificaciones_disponibles = Certificacion.objects.filter(activa=True)
    certificaciones_obtenidas = CertificacionObtenida.objects.filter(user=user).select_related('certificacion')
    certificaciones_obtenidas_ids = list(certificaciones_obtenidas.values_list('certificacion_id', flat=True))
    
    # Verificar si el usuario cumple con los requisitos para certificaciones no obtenidas
    certificaciones_disponibles_con_estado = []
    for cert in certificaciones_disponibles:
        ya_obtenida = cert.id in certificaciones_obtenidas_ids
        cumple_requisitos = verificar_requisitos_certificacion(user, cert)
        
        certificaciones_disponibles_con_estado.append({
            'certificacion': cert,
            'ya_obtenida': ya_obtenida,
            'cumple_requisitos': cumple_requisitos,
        })
    
    context = {
        'certificaciones': certificaciones_disponibles_con_estado,
        'certificaciones_obtenidas': certificaciones_obtenidas,
        'total_obtenidas': certificaciones_obtenidas.count(),
    }
    return render(request, 'core/certificaciones_lista.html', context)

@login_required
def obtener_certificacion(request, certificacion_id):
    """Obtener una certificación si se cumplen los requisitos"""
    certificacion = get_object_or_404(Certificacion, id=certificacion_id, activa=True)
    user = request.user
    
    # Verificar si ya la tiene
    if CertificacionObtenida.objects.filter(user=user, certificacion=certificacion).exists():
        messages.warning(request, 'Ya tienes esta certificación.')
        return redirect('core:certificaciones_lista')
    
    # Verificar requisitos
    if not verificar_requisitos_certificacion(user, certificacion):
        messages.error(request, 'No cumples con los requisitos para obtener esta certificación.')
        return redirect('core:certificaciones_lista')
    
    # Crear certificación
    import uuid
    codigo = f"{certificacion.nombre[:3].upper()}-{uuid.uuid4().hex[:8].upper()}"
    
    certificacion_obtenida = CertificacionObtenida.objects.create(
        user=user,
        certificacion=certificacion,
        codigo_verificacion=codigo,
        url_verificacion=f"/verificar-certificacion/{codigo}"
    )
    
    # Agregar a la lista del usuario
    if not user.certificaciones:
        user.certificaciones = []
    user.certificaciones.append(certificacion.nombre)
    user.save()
    
    messages.success(request, f'¡Felicidades! Has obtenido la certificación "{certificacion.nombre}"')
    return redirect('core:certificaciones_lista')

def verificar_certificacion(request, codigo):
    """Verificar una certificación por código"""
    certificacion = get_object_or_404(CertificacionObtenida, codigo_verificacion=codigo)
    
    context = {
        'certificacion': certificacion,
        'usuario': certificacion.user,
        'valida': True,
    }
    return render(request, 'core/verificar_certificacion.html', context)

def verificar_requisitos_certificacion(user, certificacion):
    """Verifica si un usuario cumple con los requisitos de una certificación"""
    requisitos = certificacion.requisitos
    
    # Verificar puntos requeridos
    if requisitos.get('puntos_minimos', 0) > user.points:
        return False
    
    # Verificar nivel requerido
    if requisitos.get('nivel_requerido', 1) > user.nivel_experiencia:
        return False
    
    # Verificar ejercicios completados
    if requisitos.get('ejercicios_minimos', 0) > user.total_ejercicios_completados:
        return False
    
    # Verificar tasa de aciertos
    if requisitos.get('tasa_aciertos_minima', 0) > user.tasa_aciertos:
        return False
    
    return True

# ==================== DASHBOARD DE GAMIFICACIÓN (COMPLETO) ====================

@login_required
def dashboard_gamificacion(request):
    """Dashboard de gamificación con logros, medallas y certificaciones"""
    user = request.user
    
    # Logros
    logros_disponibles = Logro.objects.all()
    logros_obtenidos = LogroObtenido.objects.filter(user=user)
    logros_obtenidos_ids = list(logros_obtenidos.values_list('logro_id', flat=True))
    
    # Estadísticas
    total_ejercicios = EjercicioLinguistico.objects.count()
    total_completados = Respuesta.objects.filter(user=user).values('item_id').distinct().count()
    
    respuestas_correctas = Respuesta.objects.filter(user=user, es_correcta=True).count()
    respuestas_totales = Respuesta.objects.filter(user=user).count()
    tasa_aciertos = int((respuestas_correctas / respuestas_totales) * 100) if respuestas_totales > 0 else 0
    
    # Evaluaciones disponibles
    evaluaciones_disponibles = Evaluacion.objects.filter(
        activa=True,
        nivel_requerido__lte=user.nivel_experiencia
    )[:5]
    
    # Actividades recomendadas
    ejercicios_completados_ids = Respuesta.objects.filter(
        user=user
    ).values_list('item_id', flat=True)
    
    actividades_recomendadas = EjercicioLinguistico.objects.exclude(
        id__in=ejercicios_completados_ids
    ).order_by('?')[:5]
    
    # Ranking
    ranking_estudiantes = User.objects.filter(
        is_staff=False
    ).order_by('-points')[:10]
    
    # Medallas y certificaciones del usuario
    user_medallas = user.medallas if user.medallas else []
    user_certificaciones = user.certificaciones if user.certificaciones else []
    
    # Certificaciones obtenidas
    certificaciones_obtenidas = CertificacionObtenida.objects.filter(user=user).select_related('certificacion')
    
    # Siguiente nivel
    siguiente_nivel = user.nivel_experiencia + 1
    puntos_para_siguiente = siguiente_nivel * 100
    
    context = {
        'user': user,
        'logros_disponibles': logros_disponibles,
        'logros_obtenidos': logros_obtenidos,
        'logros_obtenidos_ids': logros_obtenidos_ids,
        'total_ejercicios': total_ejercicios,
        'total_completados': total_completados,
        'tasa_aciertos': tasa_aciertos,
        'evaluaciones_disponibles': evaluaciones_disponibles,
        'actividades_recomendadas': actividades_recomendadas,
        'ranking_estudiantes': ranking_estudiantes,
        'user_medallas': user_medallas,
        'user_certificaciones': user_certificaciones,
        'certificaciones_obtenidas': certificaciones_obtenidas,
        'puntos_para_siguiente': puntos_para_siguiente,
        'siguiente_nivel': siguiente_nivel,
    }
    
    return render(request, 'core/dashboard_gamificacion.html', context)

# ==================== FUNCIONES AUXILIARES ====================

def verificar_logros(user):
    """Verifica y otorga logros automáticamente"""
    logros_disponibles = Logro.objects.all()
    
    for logro in logros_disponibles:
        # Verificar si ya tiene el logro
        if LogroObtenido.objects.filter(user=user, logro=logro).exists():
            continue
        
        # Verificar requisitos
        cumple_requisitos = True
        
        if logro.puntos_requeridos > 0 and user.points < logro.puntos_requeridos:
            cumple_requisitos = False
        
        if logro.nivel_requerido > 0 and user.nivel_experiencia < logro.nivel_requerido:
            cumple_requisitos = False
        
        if logro.ejercicios_completados_requeridos > 0:
            completados = Respuesta.objects.filter(
                user=user, es_correcta=True
            ).values('item_id').distinct().count()
            if completados < logro.ejercicios_completados_requeridos:
                cumple_requisitos = False
        
        if cumple_requisitos:
            # Otorgar logro
            LogroObtenido.objects.create(
                user=user,
                logro=logro
            )
            
            # Añadir a la lista del usuario
            if logro.tipo == 'medalla':
                if not user.medallas:
                    user.medallas = []
                user.medallas.append(logro.nombre)
            elif logro.tipo == 'certificacion':
                if not user.certificaciones:
                    user.certificaciones = []
                user.certificaciones.append(logro.nombre)
            elif logro.tipo == 'estrella':
                user.estrellas += 1
            
            user.save()

def ver_tecnicas(request):
    """Vista para mostrar técnicas"""
    from .models import TecnicaLinguistica
    tecnicas = TecnicaLinguistica.objects.all()
    return render(request, 'core/tecnicas.html', {'tecnicas': tecnicas})

def practicar_ejercicio(request, ejercicio_id):
    """Vista para practicar un ejercicio específico"""
    from django.shortcuts import get_object_or_404, render
    from .models import EjercicioLinguistico
    
    ejercicio = get_object_or_404(EjercicioLinguistico, id=ejercicio_id)
    
    # Procesar contenido
    contenido = ejercicio.contenido if isinstance(ejercicio.contenido, dict) else {}
    
    context = {
        'ejercicio': ejercicio,
        'contenido': contenido,
    }
    
    return render(request, 'core/practicar_ejercicio.html', context)

def dashboard_estudiante(request):
    """Dashboard del estudiante con ejercicios y técnicas"""
    from django.shortcuts import render
    from .models import EjercicioLinguistico, TecnicaLinguistica
    
    # Obtener ejercicios y técnicas
    ejercicios = EjercicioLinguistico.objects.all().order_by('?')[:12]  # 12 aleatorios
    tecnicas = TecnicaLinguistica.objects.all()
    
    context = {
        'ejercicios': ejercicios,
        'ejercicios_count': EjercicioLinguistico.objects.count(),
        'tecnicas': tecnicas,
        'tecnicas_count': tecnicas.count(),
        'puntos_total': 0,  # Aquí puedes calcular puntos reales
        'certificaciones_count': 0,  # Aquí puedes contar certificaciones reales
    }
    
    return render(request, 'core/dashboard_estudiante.html', context)

# ============================================================
# VISTAS DE AUTENTICACIÓN
# ============================================================

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('dashboard_estudiante')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'✅ ¡Bienvenido {user.username}!')
            return redirect('dashboard_estudiante')
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos')
    
    return render(request, 'core/login.html')

def registro_view(request):
    """Vista de registro de usuarios"""
    if request.user.is_authenticated:
        return redirect('dashboard_estudiante')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validaciones
        if password1 != password2:
            messages.error(request, '❌ Las contraseñas no coinciden')
            return render(request, 'core/registro.html')
        
        if len(password1) < 6:
            messages.error(request, '❌ La contraseña debe tener al menos 6 caracteres')
            return render(request, 'core/registro.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '❌ El nombre de usuario ya existe')
            return render(request, 'core/registro.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '❌ El email ya está registrado')
            return render(request, 'core/registro.html')
        
        # Crear usuario
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            messages.success(request, f'✅ ¡Usuario {username} creado exitosamente!')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'❌ Error al crear usuario: {str(e)}')
    
    return render(request, 'core/registro.html')

def logout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    messages.info(request, '👋 Sesión cerrada exitosamente')
    return redirect('index')

def perfil_usuario(request):
    """Vista del perfil del usuario"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {
        'user': request.user,
    }
    return render(request, 'core/perfil_usuario.html', context)

def editar_perfil(request):
    """Vista para editar perfil"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        user = request.user
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        messages.success(request, '✅ Perfil actualizado exitosamente')
        return redirect('perfil_usuario')
    
    return render(request, 'core/editar_perfil.html', {'user': request.user})

def cambiar_contrasena(request):
    """Vista para cambiar contraseña"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual')
        password_nueva = request.POST.get('password_nueva')
        password_confirm = request.POST.get('password_confirm')
        
        user = request.user
        
        if not user.check_password(password_actual):
            messages.error(request, '❌ Contraseña actual incorrecta')
            return render(request, 'core/cambiar_contrasena.html')
        
        if password_nueva != password_confirm:
            messages.error(request, '❌ Las nuevas contraseñas no coinciden')
            return render(request, 'core/cambiar_contrasena.html')
        
        if len(password_nueva) < 6:
            messages.error(request, '❌ La nueva contraseña debe tener al menos 6 caracteres')
            return render(request, 'core/cambiar_contrasena.html')
        
        user.set_password(password_nueva)
        user.save()
        
        messages.success(request, '✅ Contraseña actualizada exitosamente')
        return redirect('login')
    
    return render(request, 'core/cambiar_contrasena.html')

def enviar_respuesta(request, ejercicio_id):
    """Vista para enviar una respuesta a un ejercicio"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from .models import EjercicioLinguistico
    
    if request.method != 'POST':
        return redirect('practicar_ejercicio', ejercicio_id=ejercicio_id)
    
    ejercicio = get_object_or_404(EjercicioLinguistico, id=ejercicio_id)
    respuesta = request.POST.get('respuesta', '').strip()
    
    if respuesta:
        messages.success(request, f'✅ Respuesta enviada para: {ejercicio.titulo}')
    else:
        messages.warning(request, '⚠️ Por favor, escribe una respuesta')
    
    return redirect('practicar_ejercicio', ejercicio_id=ejercicio_id)

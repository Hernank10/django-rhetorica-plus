import json, random, os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from .models import User, Respuesta, ProgresoCategoria
from .forms import RegistroForm
from .decorators import admin_required

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, 'data', 'retorica.json'), 'r', encoding='utf-8') as f:
    RETORICA_DATA = json.load(f)
with open(os.path.join(BASE_DIR, 'data', 'etimologia.json'), 'r', encoding='utf-8') as f:
    ETIMOLOGIA_DATA = json.load(f)

def index(request):
    return render(request, 'core/index.html')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registro exitoso')
            return redirect('dashboard')
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciales incorrectas')
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def dashboard(request):
    total = Respuesta.objects.filter(user=request.user).count()
    correctas = Respuesta.objects.filter(user=request.user, es_correcta=True).count()
    porcentaje = round((correctas / total) * 100) if total else 0
    progreso = ProgresoCategoria.objects.filter(user=request.user)
    ultimas = Respuesta.objects.filter(user=request.user).order_by('-fecha')[:10]
    recomendaciones = []
    if total < 20:
        recomendaciones.append("Completa más ejercicios para ganar puntos")
    return render(request, 'core/dashboard.html', {
        'usuario': request.user, 'total': total, 'correctas': correctas,
        'porcentaje': porcentaje, 'progreso': progreso, 'ultimas': ultimas,
        'recomendaciones': recomendaciones
    })

@login_required
def retorica(request):
    return render(request, 'core/retorica.html', {'figuras': RETORICA_DATA})

@login_required
def etimologia(request):
    return render(request, 'core/etimologia.html', {'raices': ETIMOLOGIA_DATA})

@login_required
def examen_form(request):
    if request.method == 'POST':
        tema = request.POST.get('tema')
        num = int(request.POST.get('num_preguntas', 10))
        return render(request, 'core/examen.html', {'tema': tema, 'num': num})
    return render(request, 'core/examen_form.html')

@csrf_exempt
@login_required
def api_generar_preguntas(request):
    data = json.loads(request.body)
    tema = data.get('tema')
    num = data.get('num', 10)
    fuente = RETORICA_DATA if tema == 'retorica' else ETIMOLOGIA_DATA
    items = random.sample(fuente, min(num, len(fuente)))
    preguntas = []
    for item in items:
        if tema == 'retorica':
            respuesta = item['name']
            otros = [f for f in RETORICA_DATA if f['name'] != respuesta]
            distractores = [f['name'] for f in random.sample(otros, min(3, len(otros)))]
            pregunta = f"¿Qué figura es? {item['teoria'][:80]}..."
            categoria = item.get('category', 'Retórica')
        else:
            respuesta = item['element']
            otros = [r for r in ETIMOLOGIA_DATA if r['element'] != respuesta]
            distractores = [r['element'] for r in random.sample(otros, min(3, len(otros)))]
            pregunta = f"¿Qué raíz significa '{item['meaning']}'?"
            categoria = 'Etimología'
        opciones = [respuesta] + distractores[:3]
        random.shuffle(opciones)
        preguntas.append({'id': item['id'], 'pregunta': pregunta,
                          'respuesta_correcta': respuesta, 'opciones': opciones,
                          'categoria': categoria})
    return JsonResponse(preguntas, safe=False)

@csrf_exempt
@login_required
def api_guardar_respuesta(request):
    data = json.loads(request.body)
    puntos = 10 if data.get('es_correcta') else 0
    Respuesta.objects.create(user=request.user, tipo_ejercicio=data.get('tipo','examen'),
                             item_id=data.get('item_id'),
                             respuesta_usuario=data.get('respuesta_usuario'),
                             es_correcta=data.get('es_correcta'), puntuacion=puntos)
    request.user.points += puntos
    request.user.save()
    cat = data.get('categoria', 'General')
    prog, _ = ProgresoCategoria.objects.get_or_create(user=request.user, categoria=cat)
    prog.intentos += 1
    if data.get('es_correcta'):
        prog.aciertos += 1
    prog.save()
    return JsonResponse({'success': True, 'puntos': puntos})

@login_required
@admin_required
def admin_panel(request):
    usuarios = User.objects.all()
    total_resp = Respuesta.objects.count()
    total_pts = Respuesta.objects.aggregate(total=models.Sum('puntuacion'))['total'] or 0
    stats = []
    for u in usuarios:
        resp = Respuesta.objects.filter(user=u).count()
        corr = Respuesta.objects.filter(user=u, es_correcta=True).count()
        stats.append({
            'id': u.id, 'username': u.username, 'email': u.email,
            'respuestas': resp, 'correctas': corr, 'puntos': u.points,
            'nivel': u.nivel, 'is_admin': u.is_admin,
            'fecha_registro': u.date_joined
        })
    return render(request, 'core/admin_panel.html', {
        'usuarios': stats, 'total_usuarios': len(usuarios),
        'total_respuestas': total_resp, 'total_puntos': total_pts
    })

@login_required
@admin_required
def admin_nuevo_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        is_admin = request.POST.get('is_admin') == 'on'
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuario ya existe')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email ya registrado')
        else:
            user = User.objects.create_user(username=username, email=email, password=password, is_admin=is_admin)
            messages.success(request, f'Usuario {username} creado')
            return redirect('admin_panel')
    return render(request, 'core/admin_nuevo_usuario.html')

@login_required
@admin_required
def toggle_admin(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'No puedes cambiarte a ti mismo')
    else:
        user.is_admin = not user.is_admin
        user.save()
        messages.success(request, f'Privilegios actualizados para {user.username}')
    return redirect('admin_panel')

@login_required
@admin_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'No puedes eliminarte')
    else:
        user.delete()
        messages.success(request, f'Usuario {user.username} eliminado')
    return redirect('admin_panel')

@login_required
def proyecto(request):
    return render(request, 'core/proyecto.html')

#!/usr/bin/env python
"""
Script de prueba completo para Django Rhetorica Plus
Ejecuta: python test_app_final.py
"""

import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.db import connection
from django.apps import apps

# Importar modelos con los nombres correctos
from core.models import (
    EjercicioLinguistico,
    TecnicaLinguistica,
    ContenidoJSON,
    Evaluacion,
    Logro,
    Respuesta,
    ProgresoCategoria,
    ResultadoEvaluacion,
    LogroObtenido,
    Certificacion,
    CertificacionObtenida
)

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(title, status, message=""):
    color = Color.GREEN if status else Color.RED
    status_text = "✅ PASÓ" if status else "❌ FALLÓ"
    print(f"{color}{status_text}{Color.END} - {Color.BOLD}{title}{Color.END}")
    if message:
        print(f"   {message}")

def print_section(title):
    print(f"\n{Color.CYAN}{'='*60}{Color.END}")
    print(f"{Color.BOLD}{title}{Color.END}")
    print(f"{Color.CYAN}{'='*60}{Color.END}")

def run_tests():
    print(f"\n{Color.BOLD}{Color.BLUE}🚀 INICIANDO PRUEBAS DE DJANGO RHETORICA PLUS{Color.END}")
    print(f"{Color.CYAN}{'='*60}{Color.END}")
    
    client = Client()
    user = None
    test_data = {}
    passed = 0
    failed = 0
    
    # PRUEBA 1: Conexión a BD
    print_section("PRUEBA 1: CONEXIÓN A LA BASE DE DATOS")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print_test("Conexión a base de datos", True, f"✅ Resultado: {result[0]}")
            passed += 1
    except Exception as e:
        print_test("Conexión a base de datos", False, f"❌ Error: {str(e)[:50]}")
        failed += 1
    
    # PRUEBA 2: Modelos
    print_section("PRUEBA 2: VERIFICAR MODELOS")
    models = {
        'EjercicioLinguistico': EjercicioLinguistico,
        'TecnicaLinguistica': TecnicaLinguistica,
        'ContenidoJSON': ContenidoJSON,
        'Evaluacion': Evaluacion,
        'Logro': Logro,
        'Respuesta': Respuesta,
        'ProgresoCategoria': ProgresoCategoria,
        'ResultadoEvaluacion': ResultadoEvaluacion,
        'LogroObtenido': LogroObtenido,
        'Certificacion': Certificacion,
        'CertificacionObtenida': CertificacionObtenida
    }
    
    for name, model in models.items():
        try:
            count = model.objects.count()
            print_test(f"Modelo {name}", True, f"✅ {count} registros")
            passed += 1
        except Exception as e:
            print_test(f"Modelo {name}", False, f"❌ Error: {str(e)[:50]}")
            failed += 1
    
    # PRUEBA 3: Crear usuario
    print_section("PRUEBA 3: CREAR USUARIO")
    User.objects.filter(username='testuser').delete()
    try:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )
        print_test("Crear usuario", True, f"✅ Usuario: {user.username} (ID: {user.id})")
        passed += 1
    except Exception as e:
        print_test("Crear usuario", False, f"❌ Error: {str(e)[:50]}")
        failed += 1
    
    # PRUEBA 4: Login
    print_section("PRUEBA 4: LOGIN DE USUARIO")
    try:
        response = client.post('/login/', {
            'username': 'testuser',
            'password': 'TestPassword123!'
        })
        if response.status_code == 302:
            print_test("Login de usuario", True, f"✅ Login exitoso (status: {response.status_code})")
            passed += 1
        else:
            print_test("Login de usuario", False, f"❌ Login falló (status: {response.status_code})")
            failed += 1
    except Exception as e:
        print_test("Login de usuario", False, f"❌ Error: {str(e)[:50]}")
        failed += 1
    
    # PRUEBA 5: URLs
    print_section("PRUEBA 5: VERIFICAR URLs")
    urls_to_test = [
        ('/', 'index'),
        ('/login/', 'login'),
        ('/registro/', 'registro'),
        ('/dashboard/', 'dashboard'),
        ('/admin/', 'admin'),
    ]
    
    for url, name in urls_to_test:
        try:
            response = client.get(url)
            if response.status_code != 404:
                print_test(f"URL {url}", True, f"✅ {response.status_code}")
                passed += 1
            else:
                print_test(f"URL {url}", False, f"❌ {response.status_code}")
                failed += 1
        except Exception as e:
            print_test(f"URL {url}", False, f"❌ Error: {str(e)[:50]}")
            failed += 1
    
    # PRUEBA 6: Crear datos de prueba
    print_section("PRUEBA 6: CREAR DATOS DE PRUEBA")
    
    # Crear técnica
    try:
        tecnica = TecnicaLinguistica.objects.create(
            nombre='Técnica de Prueba',
            descripcion='Descripción de prueba',
            categoria='PRUEBA'
        )
        test_data['tecnica'] = tecnica
        print_test("Crear técnica", True, f"✅ {tecnica.nombre} (ID: {tecnica.id})")
        passed += 1
    except Exception as e:
        print_test("Crear técnica", False, f"❌ Error: {str(e)[:50]}")
        failed += 1
    
    # Crear ejercicio
    try:
        ejercicio = EjercicioLinguistico.objects.create(
            titulo='Ejercicio de Prueba',
            descripcion='Descripción de prueba',
            contenido='Contenido de prueba',
            dificultad=1,
            tecnica=test_data.get('tecnica')
        )
        test_data['ejercicio'] = ejercicio
        print_test("Crear ejercicio", True, f"✅ {ejercicio.titulo} (ID: {ejercicio.id})")
        passed += 1
    except Exception as e:
        print_test("Crear ejercicio", False, f"❌ Error: {str(e)[:50]}")
        failed += 1
    
    # PRUEBA 7: API endpoints
    print_section("PRUEBA 7: ENDPOINTS DE API")
    api_urls = [
        '/api/ejercicios/',
        '/api/tecnicas/',
        '/api/contenidos/',
    ]
    
    for url in api_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print_test(f"API {url}", True, f"✅ {response.status_code}")
                passed += 1
            else:
                print_test(f"API {url}", False, f"❌ {response.status_code}")
                failed += 1
        except Exception as e:
            print_test(f"API {url}", False, f"❌ Error: {str(e)[:50]}")
            failed += 1
    
    # PRUEBA 8: Templates
    print_section("PRUEBA 8: TEMPLATES")
    templates = [
        'core/index.html',
        'core/login.html',
        'core/registro.html',
        'core/dashboard_estudiante.html',
    ]
    
    for template in templates:
        try:
            from django.template.loader import get_template
            get_template(template)
            print_test(f"Template {template}", True, "✅ Encontrado")
            passed += 1
        except Exception as e:
            print_test(f"Template {template}", False, f"❌ No encontrado")
            failed += 1
    
    # Resumen final
    print(f"\n{Color.CYAN}{'='*60}{Color.END}")
    print(f"{Color.BOLD}RESUMEN FINAL{Color.END}")
    print(f"{Color.CYAN}{'='*60}{Color.END}")
    print(f"✅ Pruebas exitosas: {Color.GREEN}{passed}{Color.END}")
    print(f"❌ Pruebas fallidas: {Color.RED}{failed}{Color.END}")
    total = passed + failed
    print(f"📊 Total: {total} pruebas")
    
    if failed == 0:
        print(f"\n{Color.GREEN}{Color.BOLD}🎉 ¡TODAS LAS PRUEBAS PASARON!{Color.END}")
    else:
        print(f"\n{Color.RED}{Color.BOLD}⚠️ Algunas pruebas fallaron. Revisa los errores.{Color.END}")
    
    print(f"\n{Color.BOLD}📋 RECOMENDACIONES:{Color.END}")
    if not user:
        print("- Crea un superusuario: python manage.py createsuperuser")
    print("- Inicia el servidor: python manage.py runserver")
    print("- Accede a: http://localhost:8000/login/")
    print("- Usa testuser / TestPassword123! para probar")

if __name__ == "__main__":
    run_tests()

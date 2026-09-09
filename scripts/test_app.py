#!/usr/bin/env python
"""
Script de prueba completo para Django Rhetorica Plus
Ejecuta: python test_app.py
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.db import connection
from django.core.management import call_command

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Importar modelos después de configurar Django
from core.models import Ejercicio, Tecnica, Contenido, Evaluacion, Logro, Perfil, Gamificacion

class Color:
    """Colores para la terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(title, status, message=""):
    """Imprimir resultado de prueba"""
    color = Color.GREEN if status else Color.RED
    status_text = "✅ PASÓ" if status else "❌ FALLÓ"
    print(f"{color}{status_text}{Color.END} - {Color.BOLD}{title}{Color.END}")
    if message:
        print(f"   {message}")

def print_section(title):
    """Imprimir sección"""
    print(f"\n{Color.CYAN}{'='*60}{Color.END}")
    print(f"{Color.BOLD}{title}{Color.END}")
    print(f"{Color.CYAN}{'='*60}{Color.END}")

class AppTester:
    """Clase para probar la aplicación"""
    
    def __init__(self):
        self.client = Client()
        self.user = None
        self.results = []
        self.test_data = {}
    
    def test_database_connection(self):
        """Prueba 1: Conexión a la base de datos"""
        print_section("PRUEBA 1: CONEXIÓN A LA BASE DE DATOS")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                status = True
                message = f"✅ Conexión exitosa - Resultado: {result[0]}"
        except Exception as e:
            status = False
            message = f"❌ Error de conexión: {str(e)}"
        print_test("Conexión a base de datos", status, message)
        return status
    
    def test_models_exist(self):
        """Prueba 2: Verificar modelos"""
        print_section("PRUEBA 2: VERIFICAR MODELOS")
        
        models = {
            'Ejercicio': Ejercicio,
            'Tecnica': Tecnica,
            'Contenido': Contenido,
            'Evaluacion': Evaluacion,
            'Logro': Logro,
            'Perfil': Perfil,
            'Gamificacion': Gamificacion
        }
        
        all_ok = True
        for name, model in models.items():
            try:
                count = model.objects.count()
                status = True
                message = f"✅ {name}: {count} registros"
            except Exception as e:
                status = False
                message = f"❌ {name}: Error - {str(e)[:50]}"
                all_ok = False
            print_test(f"Modelo {name}", status, message)
        
        return all_ok
    
    def test_create_user(self):
        """Prueba 3: Crear usuario"""
        print_section("PRUEBA 3: CREAR USUARIO")
        
        # Limpiar usuario existente
        User.objects.filter(username='testuser').delete()
        
        try:
            # Crear usuario
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='TestPassword123!'
            )
            self.user = user
            status = True
            message = f"✅ Usuario creado: {user.username} (ID: {user.id})"
        except Exception as e:
            status = False
            message = f"❌ Error creando usuario: {str(e)}"
        
        print_test("Crear usuario", status, message)
        return status
    
    def test_user_login(self):
        """Prueba 4: Login de usuario"""
        print_section("PRUEBA 4: LOGIN DE USUARIO")
        
        if not self.user:
            print_test("Login de usuario", False, "No hay usuario para probar")
            return False
        
        try:
            # Intentar login
            response = self.client.post('/login/', {
                'username': 'testuser',
                'password': 'TestPassword123!'
            })
            status = response.status_code == 302  # Redirección después de login
            message = f"✅ Login exitoso (status: {response.status_code})" if status else f"❌ Login falló (status: {response.status_code})"
        except Exception as e:
            status = False
            message = f"❌ Error en login: {str(e)}"
        
        print_test("Login de usuario", status, message)
        return status
    
    def test_urls(self):
        """Prueba 5: Verificar URLs"""
        print_section("PRUEBA 5: VERIFICAR URLs")
        
        urls_to_test = [
            ('/', 'index'),
            ('/login/', 'login'),
            ('/registro/', 'registro'),
            ('/dashboard/', 'dashboard_estudiante'),
            ('/admin/', 'admin'),
        ]
        
        all_ok = True
        for url, name in urls_to_test:
            try:
                response = self.client.get(url)
                status = response.status_code != 404
                message = f"✅ {url} -> {response.status_code}"
                if response.status_code == 302:
                    message += f" (redirige a: {response.url})"
            except Exception as e:
                status = False
                message = f"❌ {url} -> Error: {str(e)[:50]}"
                all_ok = False
            
            print_test(f"URL {url}", status, message)
        
        return all_ok
    
    def test_create_data(self):
        """Prueba 6: Crear datos de prueba"""
        print_section("PRUEBA 6: CREAR DATOS DE PRUEBA")
        
        try:
            # Crear técnica
            tecnica = Tecnica.objects.create(
                nombre='Técnica de Prueba',
                descripcion='Descripción de prueba',
                categoria='PRUEBA'
            )
            self.test_data['tecnica'] = tecnica
            print_test("Crear técnica", True, f"✅ {tecnica.nombre} (ID: {tecnica.id})")
        except Exception as e:
            print_test("Crear técnica", False, f"❌ Error: {str(e)[:50]}")
        
        try:
            # Crear ejercicio
            ejercicio = Ejercicio.objects.create(
                titulo='Ejercicio de Prueba',
                descripcion='Descripción de prueba',
                contenido='Contenido de prueba',
                dificultad=1,
                tecnica=self.test_data.get('tecnica')
            )
            self.test_data['ejercicio'] = ejercicio
            print_test("Crear ejercicio", True, f"✅ {ejercicio.titulo} (ID: {ejercicio.id})")
        except Exception as e:
            print_test("Crear ejercicio", False, f"❌ Error: {str(e)[:50]}")
        
        try:
            # Crear contenido
            contenido = Contenido.objects.create(
                titulo='Contenido de Prueba',
                descripcion='Descripción de prueba',
                contenido='Contenido HTML de prueba',
                tipo='teoria',
                tecnica=self.test_data.get('tecnica')
            )
            self.test_data['contenido'] = contenido
            print_test("Crear contenido", True, f"✅ {contenido.titulo} (ID: {contenido.id})")
        except Exception as e:
            print_test("Crear contenido", False, f"❌ Error: {str(e)[:50]}")
        
        return True
    
    def test_data_relationships(self):
        """Prueba 7: Verificar relaciones entre datos"""
        print_section("PRUEBA 7: VERIFICAR RELACIONES")
        
        try:
            # Verificar ejercicio tiene técnica
            ejercicio = self.test_data.get('ejercicio')
            if ejercicio and ejercicio.tecnica:
                status = True
                message = f"✅ Ejercicio '{ejercicio.titulo}' tiene técnica '{ejercicio.tecnica.nombre}'"
            else:
                status = False
                message = f"❌ Ejercicio no tiene técnica asignada"
            print_test("Relación Ejercicio-Técnica", status, message)
        except Exception as e:
            print_test("Relación Ejercicio-Técnica", False, f"❌ Error: {str(e)[:50]}")
        
        try:
            # Verificar contenido tiene técnica
            contenido = self.test_data.get('contenido')
            if contenido and contenido.tecnica:
                status = True
                message = f"✅ Contenido '{contenido.titulo}' tiene técnica '{contenido.tecnica.nombre}'"
            else:
                status = False
                message = f"❌ Contenido no tiene técnica asignada"
            print_test("Relación Contenido-Técnica", status, message)
        except Exception as e:
            print_test("Relación Contenido-Técnica", False, f"❌ Error: {str(e)[:50]}")
    
    def test_api_endpoints(self):
        """Prueba 8: Verificar endpoints de API"""
        print_section("PRUEBA 8: ENDPOINTS DE API")
        
        api_urls = [
            '/api/ejercicios/',
            '/api/tecnicas/',
            '/api/contenidos/',
            '/api/evaluaciones/',
        ]
        
        all_ok = True
        for url in api_urls:
            try:
                response = self.client.get(url)
                status = response.status_code == 200
                message = f"✅ {url} -> {response.status_code}"
                if status and response.content:
                    import json
                    try:
                        data = json.loads(response.content)
                        message += f" (data: {len(data)} items)" if isinstance(data, list) else ""
                    except:
                        pass
            except Exception as e:
                status = False
                message = f"❌ {url} -> Error: {str(e)[:50]}"
                all_ok = False
            print_test(f"API {url}", status, message)
        
        return all_ok
    
    def test_template_existence(self):
        """Prueba 9: Verificar existencia de templates"""
        print_section("PRUEBA 9: TEMPLATES")
        
        templates = [
            'core/index.html',
            'core/login.html',
            'core/registro.html',
            'core/dashboard_estudiante.html',
        ]
        
        all_ok = True
        for template in templates:
            try:
                from django.template.loader import get_template
                get_template(template)
                status = True
                message = f"✅ {template} encontrado"
            except Exception as e:
                status = False
                message = f"❌ {template} no encontrado"
                all_ok = False
            print_test(f"Template {template}", status, message)
        
        return all_ok
    
    def test_migrations(self):
        """Prueba 10: Verificar migraciones"""
        print_section("PRUEBA 10: MIGRACIONES")
        
        try:
            # Verificar migraciones pendientes
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            if plan:
                status = False
                message = f"❌ Hay {len(plan)} migraciones pendientes"
            else:
                status = True
                message = "✅ Todas las migraciones aplicadas"
        except Exception as e:
            status = False
            message = f"❌ Error verificando migraciones: {str(e)[:50]}"
        
        print_test("Migraciones", status, message)
        return status
    
    def test_performance(self):
        """Prueba 11: Prueba de rendimiento simple"""
        print_section("PRUEBA 11: RENDIMIENTO")
        
        import time
        try:
            start = time.time()
            count = Ejercicio.objects.count()
            elapsed = time.time() - start
            status = elapsed < 1.0
            message = f"✅ Consulta completada en {elapsed:.3f}s ({count} registros)"
            if not status:
                message = f"⚠️ Consulta lenta: {elapsed:.3f}s"
        except Exception as e:
            status = False
            message = f"❌ Error: {str(e)[:50]}"
        
        print_test("Rendimiento de consultas", status, message)
        return status
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print(f"\n{Color.BOLD}{Color.BLUE}🚀 INICIANDO PRUEBAS DE DJANGO RHETORICA PLUS{Color.END}")
        print(f"{Color.CYAN}{'='*60}{Color.END}")
        
        tests = [
            ('Conexión a BD', self.test_database_connection),
            ('Modelos', self.test_models_exist),
            ('Crear usuario', self.test_create_user),
            ('Login', self.test_user_login),
            ('URLs', self.test_urls),
            ('Crear datos', self.test_create_data),
            ('Relaciones', self.test_data_relationships),
            ('API', self.test_api_endpoints),
            ('Templates', self.test_template_existence),
            ('Migraciones', self.test_migrations),
            ('Rendimiento', self.test_performance),
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"{Color.RED}❌ Error en prueba '{name}': {str(e)}{Color.END}")
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
        
        # Recomendaciones
        print(f"\n{Color.BOLD}📋 RECOMENDACIONES:{Color.END}")
        if not self.user:
            print("- Crea un superusuario: python manage.py createsuperuser")
        if not self.test_data.get('ejercicio'):
            print("- Carga datos de prueba: python cargar_datos.py")
        print("- Inicia el servidor: python manage.py runserver")
        print("- Accede a: http://localhost:8000/login/")
        
        return failed == 0

if __name__ == "__main__":
    tester = AppTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

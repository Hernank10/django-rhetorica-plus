#!/usr/bin/env python
"""
Generador automático de cursos basado en ejercicios existentes
Ejecuta: python scripts/generar_cursos_completos.py
"""

import sys
import os
import json
import random
from datetime import datetime
from collections import Counter, defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from core.models import EjercicioLinguistico, TecnicaLinguistica
from core.models_cursos import Curso, Modulo, Leccion, ProgresoUsuario
from django.contrib.auth.models import User
from django.utils.text import slugify

class Color:
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    NEGRITA = '\033[1m'
    FIN = '\033[0m'

class GeneradorCursosCompletos:
    def __init__(self):
        self.ejercicios_por_categoria = defaultdict(list)
        self.ejercicios_por_nivel = defaultdict(list)
        self.ejercicios_por_tipo = defaultdict(list)
        self.cursos_creados = 0
        self.modulos_creados = 0
        self.lecciones_creadas = 0
        
    def cargar_ejercicios(self):
        """Cargar y organizar ejercicios desde la base de datos"""
        print(f"\n{Color.AZUL}📚 Cargando ejercicios desde la base de datos...{Color.FIN}")
        
        ejercicios = EjercicioLinguistico.objects.all()
        total = ejercicios.count()
        print(f"  ✅ {total} ejercicios encontrados")
        
        # Organizar por categoría
        for ejercicio in ejercicios:
            categoria = ejercicio.categoria or 'Sin categoría'
            self.ejercicios_por_categoria[categoria].append(ejercicio)
            
            nivel = ejercicio.nivel or 1
            self.ejercicios_por_nivel[nivel].append(ejercicio)
            
            tipo = ejercicio.tipo or 'General'
            self.ejercicios_por_tipo[tipo].append(ejercicio)
        
        # Mostrar estadísticas
        print(f"\n{Color.VERDE}📊 Estadísticas de ejercicios:{Color.FIN}")
        print(f"  Categorías: {len(self.ejercicios_por_categoria)}")
        print(f"  Niveles: {len(self.ejercicios_por_nivel)}")
        print(f"  Tipos: {len(self.ejercicios_por_tipo)}")
        
        return total > 0
    
    def generar_cursos_por_categoria(self):
        """Generar cursos basados en categorías"""
        print(f"\n{Color.MAGENTA}📚 Generando cursos por categoría...{Color.FIN}")
        
        for categoria, ejercicios in self.ejercicios_por_categoria.items():
            if len(ejercicios) < 5:
                print(f"  ⏭️ {categoria}: {len(ejercicios)} ejercicios (mínimo 5 requeridos)")
                continue
            
            # Crear curso
            titulo = f"Curso de {categoria}"
            descripcion = f"Aprende los fundamentos de {categoria} con ejercicios prácticos y teoría."
            
            # Determinar nivel basado en los ejercicios
            niveles = [e.nivel for e in ejercicios if e.nivel]
            nivel_promedio = sum(niveles) / len(niveles) if niveles else 1
            
            nivel_map = {
                0: 'principiante',
                1: 'principiante',
                2: 'intermedio',
                3: 'avanzado',
                4: 'experto',
                5: 'experto'
            }
            nivel = nivel_map.get(int(nivel_promedio), 'intermedio')
            
            # Crear el curso
            slug = slugify(titulo)
            base_slug = slug
            counter = 1
            while Curso.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            curso = Curso.objects.create(
                titulo=titulo,
                slug=slug,
                descripcion=descripcion,
                nivel=nivel,
                estado='publicado',
                duracion_estimada=len(ejercicios) * 5 // 60 + 1,  # Aprox 5 min por ejercicio
                puntos_totales=sum(e.puntos for e in ejercicios) if ejercicios else 0,
                creado_por=User.objects.first(),
                publicado_en=datetime.now()
            )
            self.cursos_creados += 1
            
            # Crear módulos (agrupar ejercicios de a 10)
            ejercicios_ordenados = sorted(ejercicios, key=lambda x: x.nivel or 1)
            modulos = [ejercicios_ordenados[i:i+10] for i in range(0, len(ejercicios_ordenados), 10)]
            
            for i, grupo in enumerate(modulos, 1):
                modulo = Modulo.objects.create(
                    curso=curso,
                    titulo=f"Módulo {i}: {categoria} - Parte {i}",
                    descripcion=f"Ejercicios sobre {categoria} - Nivel {i}",
                    orden=i
                )
                self.modulos_creados += 1
                
                # Crear lecciones para cada ejercicio
                for j, ejercicio in enumerate(grupo, 1):
                    contenido = ejercicio.contenido if isinstance(ejercicio.contenido, dict) else {}
                    
                    leccion = Leccion.objects.create(
                        modulo=modulo,
                        titulo=ejercicio.titulo or f"Ejercicio {j}",
                        contenido=contenido.get('teoria', f"Practica {ejercicio.titulo}"),
                        tipo='practica',
                        orden=j,
                        duracion_estimada=15,
                        puntos=ejercicio.puntos or 10
                    )
                    self.lecciones_creadas += 1
                    
                    # Asociar ejercicio y técnicas
                    leccion.ejercicios_relacionados.add(ejercicio)
                    
                    # Buscar técnicas relacionadas
                    if hasattr(ejercicio, 'tecnica') and ejercicio.tecnica:
                        leccion.tecnicas_relacionadas.add(ejercicio.tecnica)
                    
                    # Buscar técnicas por categoría
                    tecnicas = TecnicaLinguistica.objects.filter(categoria__icontains=categoria)
                    for tecnica in tecnicas:
                        leccion.tecnicas_relacionadas.add(tecnica)
            
            print(f"  ✅ Curso creado: {titulo} ({len(ejercicios)} ejercicios, {len(modulos)} módulos)")
    
    def generar_cursos_por_nivel(self):
        """Generar cursos basados en niveles de dificultad"""
        print(f"\n{Color.MAGENTA}📚 Generando cursos por nivel...{Color.FIN}")
        
        nivel_nombres = {
            1: 'Principiante',
            2: 'Intermedio Básico',
            3: 'Intermedio Avanzado',
            4: 'Avanzado',
            5: 'Experto'
        }
        
        for nivel, ejercicios in self.ejercicios_por_nivel.items():
            if len(ejercicios) < 8:
                print(f"  ⏭️ Nivel {nivel}: {len(ejercicios)} ejercicios (mínimo 8 requeridos)")
                continue
            
            # Obtener categorías principales de este nivel
            categorias = Counter([e.categoria for e in ejercicios if e.categoria])
            categoria_principal = categorias.most_common(1)[0][0] if categorias else 'General'
            
            titulo = f"Curso {nivel_nombres.get(nivel, f'Nivel {nivel}')} - {categoria_principal}"
            descripcion = f"Perfecciona tus habilidades en {categoria_principal} con ejercicios de nivel {nivel}."
            
            slug = slugify(titulo)
            base_slug = slug
            counter = 1
            while Curso.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            nivel_map = {
                1: 'principiante',
                2: 'intermedio',
                3: 'intermedio',
                4: 'avanzado',
                5: 'experto'
            }
            
            curso = Curso.objects.create(
                titulo=titulo,
                slug=slug,
                descripcion=descripcion,
                nivel=nivel_map.get(nivel, 'intermedio'),
                estado='publicado',
                duracion_estimada=len(ejercicios) * 5 // 60 + 1,
                puntos_totales=sum(e.puntos for e in ejercicios) if ejercicios else 0,
                creado_por=User.objects.first(),
                publicado_en=datetime.now()
            )
            self.cursos_creados += 1
            
            # Mezclar ejercicios para variedad
            ejercicios_mezclados = ejercicios.copy()
            random.shuffle(ejercicios_mezclados)
            
            modulos = [ejercicios_mezclados[i:i+10] for i in range(0, len(ejercicios_mezclados), 10)]
            
            for i, grupo in enumerate(modulos, 1):
                modulo = Modulo.objects.create(
                    curso=curso,
                    titulo=f"Módulo {i}: Práctica Nivel {nivel}",
                    descripcion=f"Ejercicios de nivel {nivel} para practicar",
                    orden=i
                )
                self.modulos_creados += 1
                
                for j, ejercicio in enumerate(grupo, 1):
                    contenido = ejercicio.contenido if isinstance(ejercicio.contenido, dict) else {}
                    
                    leccion = Leccion.objects.create(
                        modulo=modulo,
                        titulo=ejercicio.titulo or f"Ejercicio {j}",
                        contenido=contenido.get('teoria', f"Práctica nivel {nivel}"),
                        tipo='practica',
                        orden=j,
                        duracion_estimada=15,
                        puntos=ejercicio.puntos or 10
                    )
                    self.lecciones_creadas += 1
                    leccion.ejercicios_relacionados.add(ejercicio)
            
            print(f"  ✅ Curso creado: {titulo} ({len(ejercicios)} ejercicios, {len(modulos)} módulos)")
    
    def generar_curso_completo(self):
        """Generar un curso completo con todos los ejercicios"""
        print(f"\n{Color.MAGENTA}📚 Generando curso completo...{Color.FIN}")
        
        todos_ejercicios = list(EjercicioLinguistico.objects.all())
        if len(todos_ejercicios) < 10:
            print("  ⏭️ No hay suficientes ejercicios para un curso completo")
            return
        
        titulo = "Curso Completo de Retórica y Lingüística"
        descripcion = "Un curso completo que abarca todos los aspectos de la retórica y la lingüística, con ejercicios prácticos y teoría."
        
        slug = slugify(titulo)
        base_slug = slug
        counter = 1
        while Curso.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        curso = Curso.objects.create(
            titulo=titulo,
            slug=slug,
            descripcion=descripcion,
            nivel='intermedio',
            estado='publicado',
            duracion_estimada=len(todos_ejercicios) * 5 // 60 + 2,
            puntos_totales=sum(e.puntos for e in todos_ejercicios) if todos_ejercicios else 0,
            creado_por=User.objects.first(),
            publicado_en=datetime.now()
        )
        self.cursos_creados += 1
        
        # Organizar por categoría y nivel
        ejercicios_ordenados = sorted(todos_ejercicios, key=lambda x: (x.categoria or 'Z', x.nivel or 1))
        modulos = [ejercicios_ordenados[i:i+15] for i in range(0, len(ejercicios_ordenados), 15)]
        
        for i, grupo in enumerate(modulos, 1):
            # Determinar categoría principal del módulo
            categorias_modulo = Counter([e.categoria for e in grupo if e.categoria])
            cat_principal = categorias_modulo.most_common(1)[0][0] if categorias_modulo else 'General'
            
            modulo = Modulo.objects.create(
                curso=curso,
                titulo=f"Módulo {i}: {cat_principal}",
                descripcion=f"Ejercicios de {cat_principal} para practicar",
                orden=i
            )
            self.modulos_creados += 1
            
            for j, ejercicio in enumerate(grupo, 1):
                contenido = ejercicio.contenido if isinstance(ejercicio.contenido, dict) else {}
                
                leccion = Leccion.objects.create(
                    modulo=modulo,
                    titulo=ejercicio.titulo or f"Ejercicio {j}",
                    contenido=contenido.get('teoria', f"Práctica de {ejercicio.categoria or 'Retórica'}"),
                    tipo='practica',
                    orden=j,
                    duracion_estimada=15,
                    puntos=ejercicio.puntos or 10
                )
                self.lecciones_creadas += 1
                leccion.ejercicios_relacionados.add(ejercicio)
        
        print(f"  ✅ Curso completo creado: {titulo} ({len(todos_ejercicios)} ejercicios, {len(modulos)} módulos)")
    
    def ejecutar(self):
        """Ejecutar el generador completo"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}🚀 GENERADOR AUTOMÁTICO DE CURSOS{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Cargar ejercicios
        if not self.cargar_ejercicios():
            print(f"{Color.ROJO}❌ No hay ejercicios en la base de datos{Color.FIN}")
            print(f"{Color.AMARILLO}💡 Ejecuta primero: python scripts/generar_datos_prueba.py{Color.FIN}")
            return
        
        # Preguntar qué generar
        print(f"\n{Color.AMARILLO}Selecciona qué cursos generar:{Color.FIN}")
        print("1. Cursos por categoría")
        print("2. Cursos por nivel de dificultad")
        print("3. Curso completo (todos los ejercicios)")
        print("4. Todos (1, 2 y 3)")
        
        opcion = input(f"\n{Color.CYAN}Opción (1-4): {Color.FIN}")
        
        if opcion == '1':
            self.generar_cursos_por_categoria()
        elif opcion == '2':
            self.generar_cursos_por_nivel()
        elif opcion == '3':
            self.generar_curso_completo()
        elif opcion == '4':
            self.generar_cursos_por_categoria()
            self.generar_cursos_por_nivel()
            self.generar_curso_completo()
        else:
            print(f"{Color.ROJO}❌ Opción no válida{Color.FIN}")
            return
        
        # Resumen final
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}📊 RESUMEN FINAL{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"  ✅ Cursos creados: {self.cursos_creados}")
        print(f"  ✅ Módulos creados: {self.modulos_creados}")
        print(f"  ✅ Lecciones creadas: {self.lecciones_creadas}")
        print(f"  📈 Total ejercicios en base: {EjercicioLinguistico.objects.count()}")
        print(f"  📈 Total cursos ahora: {Curso.objects.count()}")
        
        print(f"\n{Color.VERDE}✅ ¡Cursos generados exitosamente!{Color.FIN}")
        print(f"\n{Color.AZUL}💡 PRÓXIMOS PASOS:{Color.FIN}")
        print(f"  1. Inicia el servidor: python manage.py runserver")
        print(f"  2. Ver cursos: http://localhost:8000/cursos/")
        print(f"  3. Dashboard: http://localhost:8000/dashboard/")

if __name__ == "__main__":
    generador = GeneradorCursosCompletos()
    generador.ejecutar()

#!/usr/bin/env python
"""
Generador de 100 cursos completos basados en ejercicios existentes
Ejecuta: python scripts/generar_100_cursos.py
"""

import sys
import os
import random
import json
from datetime import datetime, timedelta
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from core.models import EjercicioLinguistico, TecnicaLinguistica
from core.models_cursos import Curso, Modulo, Leccion, EvaluacionCurso, PreguntaEvaluacion
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

class Generador100Cursos:
    def __init__(self):
        self.ejercicios = []
        self.tecnicas = []
        self.cursos_creados = 0
        self.modulos_creados = 0
        self.lecciones_creadas = 0
        self.evaluaciones_creadas = 0
        self.preguntas_creadas = 0
        
        # Definir temas y categorías
        self.temas = [
            'Retórica Clásica', 'Retórica Moderna', 'Argumentación', 'Persuasión',
            'Oratoria', 'Discurso Político', 'Comunicación Efectiva', 'Lingüística',
            'Semántica', 'Sintaxis', 'Morfología', 'Fonética', 'Fonología',
            'Pragmática', 'Análisis del Discurso', 'Estilística', 'Poética',
            'Narratología', 'Teoría Literaria', 'Crítica Literaria'
        ]
        
        self.niveles = ['principiante', 'intermedio', 'avanzado', 'experto']
        self.duraciones = [2, 3, 4, 5, 6, 8, 10]
        
    def cargar_datos(self):
        """Cargar ejercicios y técnicas desde la base de datos"""
        print(f"\n{Color.AZUL}📚 Cargando datos desde la base de datos...{Color.FIN}")
        
        self.ejercicios = list(EjercicioLinguistico.objects.all())
        self.tecnicas = list(TecnicaLinguistica.objects.all())
        
        print(f"  ✅ Ejercicios disponibles: {len(self.ejercicios)}")
        print(f"  ✅ Técnicas disponibles: {len(self.tecnicas)}")
        
        if len(self.ejercicios) == 0:
            print(f"{Color.ROJO}❌ No hay ejercicios. Ejecuta: python scripts/generar_datos_prueba.py{Color.FIN}")
            return False
        
        if len(self.ejercicios) < 10:
            print(f"{Color.AMARILLO}⚠️ Pocos ejercicios ({len(self.ejercicios)}). Usando los disponibles.{Color.FIN}")
        
        return True
    
    def generar_curso(self, indice):
        """Generar un curso completo con módulos, lecciones y evaluaciones"""
        
        # Seleccionar tema y nivel
        tema = random.choice(self.temas)
        nivel = random.choice(self.niveles)
        duracion = random.choice(self.duraciones)
        
        # Crear título y descripción
        titulo = f"Curso {indice}: {tema} - {nivel.capitalize()}"
        descripcion = f"Domina los fundamentos de {tema} con ejercicios prácticos y teoría. Nivel {nivel}."
        
        # Crear slug único
        slug_base = slugify(f"curso-{indice}-{tema}")
        slug = slug_base
        contador = 1
        while Curso.objects.filter(slug=slug).exists():
            slug = f"{slug_base}-{contador}"
            contador += 1
        
        # Crear curso
        curso = Curso.objects.create(
            titulo=titulo,
            slug=slug,
            descripcion=descripcion,
            objetivo=f"Comprender y aplicar los conceptos fundamentales de {tema}",
            nivel=nivel,
            estado='publicado',
            duracion_estimada=duracion,
            puntos_totales=0,
            creado_por=User.objects.first(),
            publicado_en=datetime.now()
        )
        self.cursos_creados += 1
        
        # Seleccionar ejercicios para este curso
        ejercicios_curso = self.seleccionar_ejercicios_para_curso(tema, nivel)
        
        # Crear módulos (3-5 módulos por curso)
        num_modulos = random.randint(3, 5)
        ejercicios_por_modulo = max(3, len(ejercicios_curso) // num_modulos)
        
        for i in range(num_modulos):
            inicio = i * ejercicios_por_modulo
            fin = min((i + 1) * ejercicios_por_modulo, len(ejercicios_curso))
            ejercicios_modulo = ejercicios_curso[inicio:fin]
            
            if len(ejercicios_modulo) < 2:
                continue
            
            # Crear módulo
            modulo = Modulo.objects.create(
                curso=curso,
                titulo=f"Módulo {i+1}: {tema} - Parte {i+1}",
                descripcion=f"Profundiza en los conceptos de {tema} con ejercicios prácticos",
                orden=i+1
            )
            self.modulos_creados += 1
            
            # Crear lecciones
            for j, ejercicio in enumerate(ejercicios_modulo, 1):
                contenido = ejercicio.contenido if isinstance(ejercicio.contenido, dict) else {}
                
                leccion = Leccion.objects.create(
                    modulo=modulo,
                    titulo=ejercicio.titulo or f"Lección {j}",
                    contenido=contenido.get('teoria', f"Práctica de {tema}"),
                    tipo='practica',
                    orden=j,
                    duracion_estimada=15,
                    puntos=ejercicio.puntos or 10
                )
                leccion.ejercicios_relacionados.add(ejercicio)
                self.lecciones_creadas += 1
                
                # Asignar técnicas relacionadas
                if self.tecnicas:
                    tecnicas_aleatorias = random.sample(
                        self.tecnicas, 
                        min(random.randint(1, 3), len(self.tecnicas))
                    )
                    leccion.tecnicas_relacionadas.set(tecnicas_aleatorias)
            
            # Crear evaluación para el módulo (30% de los módulos)
            if random.random() < 0.3 and len(ejercicios_modulo) >= 3:
                self.crear_evaluacion(curso, modulo, ejercicios_modulo)
        
        # Actualizar puntos totales del curso
        puntos_totales = 0
        for m in curso.modulos.all():
            for l in m.lecciones.all():
                puntos_totales += l.puntos
        curso.puntos_totales = puntos_totales
        curso.save()
        
        return curso
    
    def seleccionar_ejercicios_para_curso(self, tema, nivel):
        """Seleccionar ejercicios relevantes para el curso"""
        ejercicios_curso = []
        
        # Buscar ejercicios por tema
        for ej in self.ejercicios:
            if ej.categoria and tema.lower() in ej.categoria.lower():
                ejercicios_curso.append(ej)
            elif ej.titulo and tema.lower() in ej.titulo.lower():
                ejercicios_curso.append(ej)
        
        # Si no hay ejercicios del tema, usar ejercicios aleatorios
        if len(ejercicios_curso) < 10:
            ejercicios_curso = random.sample(
                self.ejercicios, 
                min(30, len(self.ejercicios))
            )
        
        # Filtrar por nivel
        nivel_map = {
            'principiante': [1, 2],
            'intermedio': [2, 3],
            'avanzado': [3, 4],
            'experto': [4, 5]
        }
        niveles_permitidos = nivel_map.get(nivel, [1, 2, 3])
        ejercicios_curso = [e for e in ejercicios_curso if e.nivel in niveles_permitidos]
        
        # Limitar y mezclar
        ejercicios_curso = ejercicios_curso[:30]
        random.shuffle(ejercicios_curso)
        
        return ejercicios_curso
    
    def crear_evaluacion(self, curso, modulo, ejercicios):
        """Crear una evaluación para un módulo"""
        if not ejercicios:
            return
        
        num_preguntas = min(random.randint(5, 10), len(ejercicios))
        ejercicios_eval = random.sample(ejercicios, num_preguntas)
        
        evaluacion = EvaluacionCurso.objects.create(
            curso=curso,
            modulo=modulo,
            titulo=f"Evaluación: {modulo.titulo}",
            descripcion=f"Evalúa tus conocimientos sobre {curso.titulo} - {modulo.titulo}",
            tipo='formativa',
            preguntas_por_evaluacion=num_preguntas,
            tiempo_limite=random.randint(20, 45),
            puntaje_maximo=0,
            intentos_permitidos=3,
            disponible_desde=datetime.now(),
            disponible_hasta=datetime.now() + timedelta(days=30)
        )
        self.evaluaciones_creadas += 1
        
        # Crear preguntas
        puntaje_total = 0
        for i, ej in enumerate(ejercicios_eval, 1):
            contenido = ej.contenido if isinstance(ej.contenido, dict) else {}
            
            # Determinar tipo de pregunta
            tipos = ['multiple', 'desarrollo', 'verdadero_falso', 'completar']
            tipo_pregunta = random.choice(tipos)
            
            opciones = None
            if tipo_pregunta == 'multiple':
                opciones = [
                    contenido.get('suggestedAnswer', 'Opción correcta'),
                    f"Opción alternativa {i}",
                    f"Opción alternativa {i+1}",
                    f"Opción alternativa {i+2}"
                ]
                random.shuffle(opciones)
            
            pregunta = PreguntaEvaluacion.objects.create(
                evaluacion=evaluacion,
                ejercicio=ej,
                enunciado=contenido.get('ejercicio', f"Pregunta {i}"),
                tipo=tipo_pregunta,
                opciones=opciones,
                respuesta_correcta=contenido.get('suggestedAnswer', 'Respuesta correcta'),
                puntaje=random.randint(5, 15),
                orden=i
            )
            puntaje_total += pregunta.puntaje
            self.preguntas_creadas += 1
        
        evaluacion.puntaje_maximo = puntaje_total
        evaluacion.save()
    
    def generar_todos(self):
        """Generar 100 cursos completos"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}🚀 GENERADOR DE 100 CURSOS COMPLETOS{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Cargar datos
        if not self.cargar_datos():
            return
        
        # Eliminar cursos existentes
        print(f"\n{Color.AMARILLO}🗑️ Eliminando cursos existentes...{Color.FIN}")
        Curso.objects.all().delete()
        print(f"  ✅ Cursos eliminados")
        
        # Generar 100 cursos
        print(f"\n{Color.AZUL}📚 Generando 100 cursos...{Color.FIN}\n")
        
        for i in range(1, 101):
            curso = self.generar_curso(i)
            if i % 10 == 0:
                print(f"  ✅ Generados {i} cursos...")
        
        # Mostrar resumen
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}📊 RESUMEN FINAL{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"  ✅ Cursos creados: {self.cursos_creados}")
        print(f"  ✅ Módulos creados: {self.modulos_creados}")
        print(f"  ✅ Lecciones creadas: {self.lecciones_creadas}")
        print(f"  ✅ Evaluaciones creadas: {self.evaluaciones_creadas}")
        print(f"  ✅ Preguntas creadas: {self.preguntas_creadas}")
        
        # Mostrar algunos cursos de ejemplo
        print(f"\n{Color.AZUL}📋 Ejemplos de cursos generados:{Color.FIN}")
        for curso in Curso.objects.all().order_by('?')[:5]:
            modulos = curso.modulos.count()
            lecciones = 0
            for m in curso.modulos.all():
                lecciones += m.lecciones.count()
            evaluaciones = EvaluacionCurso.objects.filter(curso=curso).count()
            print(f"  - {curso.titulo}")
            print(f"    Módulos: {modulos}, Lecciones: {lecciones}, Evaluaciones: {evaluaciones}")
        
        print(f"\n{Color.VERDE}✅ ¡100 cursos generados exitosamente!{Color.FIN}")
        print(f"\n{Color.AZUL}💡 PRÓXIMOS PASOS:{Color.FIN}")
        print(f"  1. Inicia el servidor: python manage.py runserver")
        print(f"  2. Ver cursos: http://localhost:8000/cursos/")

if __name__ == "__main__":
    generador = Generador100Cursos()
    generador.generar_todos()

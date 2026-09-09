#!/usr/bin/env python
"""
Generador automático de evaluaciones para cursos
Crea evaluaciones basadas en las lecciones y ejercicios existentes
Ejecuta: python scripts/generar_evaluaciones_cursos.py
"""

import sys
import os
import json
import random
from datetime import datetime, timedelta
from collections import Counter, defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')

import django
django.setup()

from core.models import EjercicioLinguistico, TecnicaLinguistica
from core.models_cursos import Curso, Modulo, Leccion, EvaluacionCurso, PreguntaEvaluacion, ResultadoEvaluacionCurso
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

class GeneradorEvaluacionesCursos:
    def __init__(self):
        self.cursos_procesados = 0
        self.evaluaciones_creadas = 0
        self.preguntas_creadas = 0
        self.ejercicios_disponibles = []
        
    def cargar_ejercicios(self):
        """Cargar ejercicios desde la base de datos"""
        print(f"\n{Color.AZUL}📚 Cargando ejercicios...{Color.FIN}")
        
        self.ejercicios_disponibles = list(EjercicioLinguistico.objects.all())
        total = len(self.ejercicios_disponibles)
        print(f"  ✅ {total} ejercicios disponibles")
        
        # Mostrar estadísticas
        categorias = Counter([e.categoria for e in self.ejercicios_disponibles if e.categoria])
        print(f"  📂 Categorías: {len(categorias)}")
        for cat, count in categorias.most_common(5):
            print(f"    - {cat}: {count}")
        
        return total > 0
    
    def generar_evaluacion_curso(self, curso):
        """Generar evaluación para un curso"""
        print(f"\n{Color.MAGENTA}📝 Generando evaluación para: {curso.titulo}{Color.FIN}")
        
        # Obtener lecciones del curso
        lecciones = []
        for modulo in curso.modulos.all():
            lecciones.extend(modulo.lecciones.all())
        
        if not lecciones:
            print(f"  ⚠️ El curso no tiene lecciones. Ejecuta primero el generador de lecciones.")
            return False
        
        # Obtener ejercicios de las lecciones
        ejercicios_curso = []
        for leccion in lecciones:
            ejercicios_curso.extend(leccion.ejercicios_relacionados.all())
        
        # Si no hay ejercicios en las lecciones, usar ejercicios de la categoría
        if not ejercicios_curso:
            ejercicios_curso = [e for e in self.ejercicios_disponibles if e.categoria and e.categoria.lower() in curso.titulo.lower()]
        
        # Si aún no hay ejercicios, usar ejercicios por nivel
        if not ejercicios_curso:
            nivel_map = {
                'principiante': [1, 2],
                'intermedio': [2, 3],
                'avanzado': [3, 4],
                'experto': [4, 5]
            }
            niveles_buscar = nivel_map.get(curso.nivel, [1, 2, 3])
            ejercicios_curso = [e for e in self.ejercicios_disponibles if e.nivel in niveles_buscar]
        
        if not ejercicios_curso:
            print(f"  ⚠️ No hay ejercicios para crear evaluación")
            return False
        
        # Crear la evaluación
        evaluacion = EvaluacionCurso.objects.create(
            curso=curso,
            titulo=f"Evaluación de {curso.titulo}",
            descripcion=f"Evalúa tus conocimientos en {curso.titulo}",
            tipo='sumativa',
            preguntas_por_evaluacion=min(10, len(ejercicios_curso)),
            tiempo_limite=30,
            puntaje_maximo=0,  # Se calculará después
            intentos_permitidos=3,
            disponible_desde=datetime.now(),
            disponible_hasta=datetime.now() + timedelta(days=30)
        )
        self.evaluaciones_creadas += 1
        
        # Seleccionar ejercicios para las preguntas
        if len(ejercicios_curso) > evaluacion.preguntas_por_evaluacion:
            ejercicios_seleccionados = random.sample(ejercicios_curso, evaluacion.preguntas_por_evaluacion)
        else:
            ejercicios_seleccionados = ejercicios_curso
        
        # Crear preguntas
        puntaje_total = 0
        for i, ejercicio in enumerate(ejercicios_seleccionados, 1):
            contenido = ejercicio.contenido if isinstance(ejercicio.contenido, dict) else {}
            
            # Determinar tipo de pregunta según el contenido
            tipo_pregunta = self._determinar_tipo_pregunta(contenido)
            
            # Crear enunciado
            enunciado = self._crear_enunciado(ejercicio, contenido)
            
            # Obtener respuesta correcta
            respuesta_correcta = self._obtener_respuesta_correcta(contenido, ejercicio)
            
            # Crear opciones para preguntas de opción múltiple
            opciones = None
            if tipo_pregunta in ['multiple', 'opcion_multiple']:
                opciones = self._crear_opciones(ejercicio, contenido, respuesta_correcta)
                tipo_pregunta = 'multiple'
            
            pregunta = PreguntaEvaluacion.objects.create(
                evaluacion=evaluacion,
                ejercicio=ejercicio,
                enunciado=enunciado,
                tipo=tipo_pregunta,
                opciones=opciones,
                respuesta_correcta=respuesta_correcta,
                puntaje=10,
                orden=i
            )
            self.preguntas_creadas += 1
            puntaje_total += pregunta.puntaje
        
        # Actualizar puntaje máximo
        evaluacion.puntaje_maximo = puntaje_total
        evaluacion.save()
        
        print(f"  ✅ Evaluación creada: {evaluacion.titulo}")
        print(f"    - Preguntas: {self.preguntas_creadas}")
        print(f"    - Puntaje máximo: {puntaje_total}")
        
        return True
    
    def _determinar_tipo_pregunta(self, contenido):
        """Determinar el tipo de pregunta según el contenido"""
        if contenido.get('ejercicio'):
            texto = contenido['ejercicio'].lower()
            if 'elige' in texto or 'selecciona' in texto:
                return 'multiple'
            elif 'completa' in texto or '___' in texto:
                return 'completar'
            elif 'corrige' in texto or 'error' in texto:
                return 'correccion'
            elif 'explica' in texto or 'define' in texto:
                return 'desarrollo'
            elif 'verdadero' in texto or 'falso' in texto:
                return 'verdadero_falso'
        
        return 'desarrollo'
    
    def _crear_enunciado(self, ejercicio, contenido):
        """Crear enunciado para la pregunta"""
        if contenido.get('ejercicio'):
            return contenido['ejercicio']
        elif contenido.get('teoria'):
            return f"Basado en: {contenido['teoria'][:100]}"
        else:
            return f"Ejercicio: {ejercicio.titulo}"
    
    def _obtener_respuesta_correcta(self, contenido, ejercicio):
        """Obtener la respuesta correcta"""
        if contenido.get('suggestedAnswer'):
            return contenido['suggestedAnswer']
        elif contenido.get('respuesta_correcta'):
            return contenido['respuesta_correcta']
        else:
            return "Respuesta no disponible"
    
    def _crear_opciones(self, ejercicio, contenido, respuesta_correcta):
        """Crear opciones para preguntas de opción múltiple"""
        opciones = [respuesta_correcta]
        
        # Intentar obtener otras opciones del contenido
        if contenido.get('opciones'):
            for opcion in contenido['opciones']:
                if opcion not in opciones and len(opciones) < 4:
                    opciones.append(opcion)
        
        # Si no hay suficientes opciones, usar opciones genéricas
        while len(opciones) < 4:
            opciones.append(f"Opción {len(opciones) + 1}")
        
        random.shuffle(opciones)
        return opciones
    
    def generar_evaluaciones_para_todos(self):
        """Generar evaluaciones para todos los cursos"""
        cursos = Curso.objects.filter(estado='publicado')
        
        if not cursos:
            print(f"{Color.AMARILLO}⚠️ No hay cursos publicados{Color.FIN}")
            return
        
        print(f"\n{Color.CYAN}🎯 Generando evaluaciones para {len(cursos)} cursos...{Color.FIN}")
        
        for curso in cursos:
            # Verificar si ya tiene evaluaciones
            if EvaluacionCurso.objects.filter(curso=curso).exists():
                print(f"  ⏭️ {curso.titulo} ya tiene evaluaciones")
                continue
            
            if self.generar_evaluacion_curso(curso):
                self.cursos_procesados += 1
    
    def generar_desde_json(self):
        """Generar evaluaciones desde archivos JSON"""
        print(f"\n{Color.AZUL}📂 Generando evaluaciones desde JSON...{Color.FIN}")
        
        import glob
        archivos_json = glob.glob(os.path.join(BASE_DIR, '*.json'))
        archivos_ejercicios = [f for f in archivos_json if 'ejercicio' in f.lower() or 'data' in f.lower()]
        
        if not archivos_ejercicios:
            print(f"  ⚠️ No se encontraron archivos JSON")
            return 0
        
        total_importados = 0
        for archivo in archivos_ejercicios[:3]:
            try:
                print(f"  📄 Procesando: {os.path.basename(archivo)}")
                with open(archivo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                
                if isinstance(datos, dict):
                    datos = datos.get('ejercicios', [])
                
                if not datos:
                    continue
                
                # Crear un curso temporal si no existe
                curso, created = Curso.objects.get_or_create(
                    titulo="Curso desde JSON",
                    defaults={
                        'slug': 'curso-desde-json',
                        'descripcion': 'Curso generado desde archivos JSON',
                        'nivel': 'intermedio',
                        'estado': 'publicado'
                    }
                )
                
                evaluacion = EvaluacionCurso.objects.create(
                    curso=curso,
                    titulo=f"Evaluación desde JSON - {os.path.basename(archivo)}",
                    descripcion="Evaluación generada automáticamente desde archivos JSON",
                    tipo='sumativa',
                    preguntas_por_evaluacion=min(10, len(datos)),
                    tiempo_limite=30,
                    puntaje_maximo=0
                )
                self.evaluaciones_creadas += 1
                
                puntaje_total = 0
                for i, item in enumerate(datos[:10], 1):
                    contenido = item.get('contenido', {})
                    
                    pregunta = PreguntaEvaluacion.objects.create(
                        evaluacion=evaluacion,
                        enunciado=contenido.get('ejercicio', item.get('titulo', 'Sin enunciado')),
                        tipo='desarrollo',
                        respuesta_correcta=contenido.get('suggestedAnswer', ''),
                        puntaje=10,
                        orden=i
                    )
                    self.preguntas_creadas += 1
                    puntaje_total += 10
                
                evaluacion.puntaje_maximo = puntaje_total
                evaluacion.save()
                total_importados += 1
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        return total_importados
    
    def ejecutar(self):
        """Ejecutar el generador completo"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}🚀 GENERADOR DE EVALUACIONES PARA CURSOS{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Cargar ejercicios
        if not self.cargar_ejercicios():
            print(f"{Color.ROJO}❌ No hay ejercicios disponibles{Color.FIN}")
            return
        
        # Mostrar menú
        print(f"\n{Color.AMARILLO}Selecciona una opción:{Color.FIN}")
        print("1. Generar evaluaciones para todos los cursos")
        print("2. Generar evaluación para un curso específico")
        print("3. Generar evaluaciones desde archivos JSON")
        print("4. Todas las opciones")
        
        opcion = input(f"\n{Color.CYAN}Opción (1-4): {Color.FIN}")
        
        if opcion == '1':
            self.generar_evaluaciones_para_todos()
        elif opcion == '2':
            cursos = Curso.objects.filter(estado='publicado')
            print(f"\n{Color.AZUL}Cursos disponibles:{Color.FIN}")
            for i, curso in enumerate(cursos, 1):
                print(f"  {i}. {curso.titulo}")
            
            try:
                seleccion = int(input(f"\n{Color.CYAN}Selecciona el número del curso: {Color.FIN}")) - 1
                if 0 <= seleccion < len(cursos):
                    self.generar_evaluacion_curso(cursos[seleccion])
                    self.cursos_procesados += 1
            except:
                print(f"{Color.ROJO}❌ Selección inválida{Color.FIN}")
        elif opcion == '3':
            importados = self.generar_desde_json()
            print(f"  ✅ {importados} evaluaciones importadas desde JSON")
        elif opcion == '4':
            self.generar_evaluaciones_para_todos()
            importados = self.generar_desde_json()
            print(f"  ✅ {importados} evaluaciones importadas desde JSON")
        else:
            print(f"{Color.ROJO}❌ Opción no válida{Color.FIN}")
            return
        
        # Resumen final
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}📊 RESUMEN FINAL{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"  ✅ Cursos procesados: {self.cursos_procesados}")
        print(f"  ✅ Evaluaciones creadas: {self.evaluaciones_creadas}")
        print(f"  ✅ Preguntas creadas: {self.preguntas_creadas}")
        print(f"  📈 Total evaluaciones: {EvaluacionCurso.objects.count()}")
        print(f"  📈 Total preguntas: {PreguntaEvaluacion.objects.count()}")
        
        print(f"\n{Color.VERDE}✅ ¡Evaluaciones generadas exitosamente!{Color.FIN}")
        print(f"\n{Color.AZUL}💡 PRÓXIMOS PASOS:{Color.FIN}")
        print(f"  1. Inicia el servidor: python manage.py runserver")
        print(f"  2. Ver cursos: http://localhost:8000/cursos/")
        print(f"  3. Las evaluaciones estarán disponibles en cada curso")

if __name__ == "__main__":
    generador = GeneradorEvaluacionesCursos()
    generador.ejecutar()

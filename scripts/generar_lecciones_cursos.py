#!/usr/bin/env python
"""
Generador automático de lecciones para cursos existentes
Revisa cursos sin lecciones y las genera desde ejercicios disponibles
Ejecuta: python scripts/generar_lecciones_cursos.py
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

class GeneradorLeccionesCursos:
    def __init__(self):
        self.cursos_revisados = 0
        self.cursos_sin_lecciones = 0
        self.cursos_corregidos = 0
        self.modulos_creados = 0
        self.lecciones_creadas = 0
        self.ejercicios_por_categoria = defaultdict(list)
        self.ejercicios_por_nivel = defaultdict(list)
        self.ejercicios_por_tipo = defaultdict(list)
        
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
        
        return total > 0
    
    def revisar_cursos(self):
        """Revisar todos los cursos y detectar los que no tienen lecciones"""
        print(f"\n{Color.CYAN}🔍 Revisando cursos existentes...{Color.FIN}")
        
        cursos = Curso.objects.all()
        self.cursos_revisados = cursos.count()
        
        print(f"  Total cursos: {self.cursos_revisados}")
        
        cursos_sin_lecciones = []
        for curso in cursos:
            # Contar lecciones en todos los módulos
            total_lecciones = 0
            for modulo in curso.modulos.all():
                total_lecciones += modulo.lecciones.count()
            
            if total_lecciones == 0:
                cursos_sin_lecciones.append(curso)
                print(f"  ⚠️ Curso sin lecciones: {curso.titulo} (ID: {curso.id})")
        
        self.cursos_sin_lecciones = len(cursos_sin_lecciones)
        return cursos_sin_lecciones
    
    def generar_lecciones_para_curso(self, curso):
        """Generar lecciones para un curso específico"""
        print(f"\n{Color.MAGENTA}📝 Generando lecciones para: {curso.titulo}{Color.FIN}")
        
        # Determinar el nivel del curso
        nivel_curso = curso.nivel
        
        # Buscar ejercicios relevantes para este curso
        ejercicios_relevantes = []
        
        # Buscar por categoría en el título del curso
        palabras_clave = curso.titulo.lower().split()
        
        for ejercicio in EjercicioLinguistico.objects.all():
            # Verificar si el ejercicio coincide con la categoría del curso
            if ejercicio.categoria and ejercicio.categoria.lower() in curso.titulo.lower():
                ejercicios_relevantes.append(ejercicio)
            elif ejercicio.titulo and any(palabra in ejercicio.titulo.lower() for palabra in palabras_clave):
                ejercicios_relevantes.append(ejercicio)
        
        # Si no hay ejercicios relevantes, usar ejercicios por nivel
        if not ejercicios_relevantes:
            # Mapear nivel del curso a nivel de ejercicios
            nivel_map = {
                'principiante': [1, 2],
                'intermedio': [2, 3],
                'avanzado': [3, 4],
                'experto': [4, 5]
            }
            niveles_buscar = nivel_map.get(nivel_curso, [1, 2, 3])
            
            for ejercicio in EjercicioLinguistico.objects.all():
                if ejercicio.nivel in niveles_buscar:
                    ejercicios_relevantes.append(ejercicio)
        
        # Si aún no hay ejercicios, usar todos los ejercicios
        if not ejercicios_relevantes:
            ejercicios_relevantes = list(EjercicioLinguistico.objects.all())
        
        # Limitar a 50 ejercicios máximo por curso
        if len(ejercicios_relevantes) > 50:
            ejercicios_relevantes = random.sample(ejercicios_relevantes, 50)
        
        if not ejercicios_relevantes:
            print(f"  ⚠️ No hay ejercicios disponibles para {curso.titulo}")
            return False
        
        # Eliminar módulos existentes si no tienen lecciones
        for modulo in curso.modulos.all():
            if modulo.lecciones.count() == 0:
                modulo.delete()
        
        # Crear nuevos módulos
        ejercicios_ordenados = sorted(ejercicios_relevantes, key=lambda x: (x.nivel or 1, x.categoria or ''))
        ejercicios_por_modulo = 10
        grupos = [ejercicios_ordenados[i:i+ejercicios_por_modulo] for i in range(0, len(ejercicios_ordenados), ejercicios_por_modulo)]
        
        lecciones_creadas = 0
        for i, grupo in enumerate(grupos, 1):
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
                
                # Determinar tipo de lección basado en el contenido
                tipo_leccion = 'practica'
                if contenido.get('teoria') and len(contenido.get('teoria', '')) > 100:
                    tipo_leccion = 'teoria'
                elif contenido.get('ejercicio') and 'completa' in contenido.get('ejercicio', '').lower():
                    tipo_leccion = 'evaluacion'
                
                leccion = Leccion.objects.create(
                    modulo=modulo,
                    titulo=ejercicio.titulo or f"Ejercicio {j}",
                    contenido=contenido.get('teoria', f"Práctica de {ejercicio.categoria or 'Retórica'}"),
                    tipo=tipo_leccion,
                    orden=j,
                    duracion_estimada=15,
                    puntos=ejercicio.puntos or 10
                )
                self.lecciones_creadas += 1
                leccion.ejercicios_relacionados.add(ejercicio)
                lecciones_creadas += 1
                
                # Asociar técnicas relacionadas
                if hasattr(ejercicio, 'tecnica') and ejercicio.tecnica:
                    leccion.tecnicas_relacionadas.add(ejercicio.tecnica)
        
        print(f"  ✅ Creadas {lecciones_creadas} lecciones en {len(grupos)} módulos")
        return True
    
    def generar_lecciones_json(self):
        """Generar lecciones desde archivos JSON si existen"""
        print(f"\n{Color.AZUL}📂 Buscando archivos JSON...{Color.FIN}")
        
        import glob
        archivos_json = glob.glob(os.path.join(BASE_DIR, '*.json'))
        archivos_ejercicios = [f for f in archivos_json if 'ejercicio' in f.lower() or 'data' in f.lower()]
        
        if not archivos_ejercicios:
            print(f"  ⚠️ No se encontraron archivos JSON con ejercicios")
            return 0
        
        total_importados = 0
        for archivo in archivos_ejercicios[:3]:  # Limitar a 3 archivos
            try:
                print(f"  📄 Procesando: {os.path.basename(archivo)}")
                with open(archivo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                
                if isinstance(datos, dict):
                    datos = datos.get('ejercicios', [])
                
                if not datos:
                    continue
                
                # Buscar un curso que coincida con la categoría
                for item in datos[:20]:  # Limitar por archivo
                    if not isinstance(item, dict):
                        continue
                    
                    categoria = item.get('categoria', 'General')
                    titulo = item.get('titulo', 'Sin título')
                    
                    # Buscar curso que coincida con la categoría
                    curso = Curso.objects.filter(
                        titulo__icontains=categoria
                    ).first()
                    
                    if not curso:
                        curso = Curso.objects.filter(
                            descripcion__icontains=categoria
                        ).first()
                    
                    if curso:
                        # Crear módulo si no existe
                        modulo, created = Modulo.objects.get_or_create(
                            curso=curso,
                            titulo=f"Módulo: {categoria}",
                            defaults={'descripcion': f"Ejercicios de {categoria}", 'orden': 1}
                        )
                        
                        # Crear lección
                        contenido = item.get('contenido', {})
                        leccion = Leccion.objects.create(
                            modulo=modulo,
                            titulo=titulo,
                            contenido=contenido.get('teoria', f"Ejercicio de {categoria}"),
                            tipo='practica',
                            puntos=item.get('puntos', 10)
                        )
                        total_importados += 1
                        self.lecciones_creadas += 1
                
                print(f"    ✅ {total_importados} lecciones importadas")
                
            except Exception as e:
                print(f"    ❌ Error al procesar {archivo}: {e}")
        
        return total_importados
    
    def ejecutar(self):
        """Ejecutar el generador completo"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}🚀 GENERADOR DE LECCIONES PARA CURSOS{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Cargar ejercicios
        if not self.cargar_ejercicios():
            print(f"{Color.ROJO}❌ No hay ejercicios en la base de datos{Color.FIN}")
            return
        
        # Revisar cursos
        cursos_sin_lecciones = self.revisar_cursos()
        
        if not cursos_sin_lecciones:
            print(f"\n{Color.VERDE}✅ Todos los cursos tienen lecciones!{Color.FIN}")
            return
        
        print(f"\n{Color.AMARILLO}⚠️ {len(cursos_sin_lecciones)} cursos sin lecciones{Color.FIN}")
        
        # Preguntar qué hacer
        print(f"\n{Color.AMARILLO}Selecciona una opción:{Color.FIN}")
        print("1. Generar lecciones para todos los cursos sin lecciones")
        print("2. Generar lecciones para un curso específico")
        print("3. Importar lecciones desde archivos JSON")
        print("4. Todas las opciones")
        
        opcion = input(f"\n{Color.CYAN}Opción (1-4): {Color.FIN}")
        
        if opcion == '1':
            for curso in cursos_sin_lecciones:
                if self.generar_lecciones_para_curso(curso):
                    self.cursos_corregidos += 1
        elif opcion == '2':
            print(f"\n{Color.AZUL}Cursos sin lecciones:{Color.FIN}")
            for i, curso in enumerate(cursos_sin_lecciones, 1):
                print(f"  {i}. {curso.titulo} (ID: {curso.id})")
            
            try:
                seleccion = int(input(f"\n{Color.CYAN}Selecciona el número del curso: {Color.FIN}")) - 1
                if 0 <= seleccion < len(cursos_sin_lecciones):
                    if self.generar_lecciones_para_curso(cursos_sin_lecciones[seleccion]):
                        self.cursos_corregidos += 1
            except:
                print(f"{Color.ROJO}❌ Selección inválida{Color.FIN}")
        elif opcion == '3':
            importados = self.generar_lecciones_json()
            print(f"  ✅ {importados} lecciones importadas desde JSON")
        elif opcion == '4':
            # Generar lecciones para todos los cursos
            for curso in cursos_sin_lecciones:
                if self.generar_lecciones_para_curso(curso):
                    self.cursos_corregidos += 1
            
            # Importar desde JSON
            importados = self.generar_lecciones_json()
            print(f"  ✅ {importados} lecciones importadas desde JSON")
        else:
            print(f"{Color.ROJO}❌ Opción no válida{Color.FIN}")
            return
        
        # Resumen final
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}📊 RESUMEN FINAL{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"  ✅ Cursos revisados: {self.cursos_revisados}")
        print(f"  ✅ Cursos sin lecciones: {self.cursos_sin_lecciones}")
        print(f"  ✅ Cursos corregidos: {self.cursos_corregidos}")
        print(f"  ✅ Módulos creados: {self.modulos_creados}")
        print(f"  ✅ Lecciones creadas: {self.lecciones_creadas}")
        print(f"  📈 Total cursos ahora: {Curso.objects.count()}")
        print(f"  📈 Total lecciones ahora: {Leccion.objects.count()}")
        
        print(f"\n{Color.VERDE}✅ ¡Lecciones generadas exitosamente!{Color.FIN}")
        print(f"\n{Color.AZUL}💡 PRÓXIMOS PASOS:{Color.FIN}")
        print(f"  1. Inicia el servidor: python manage.py runserver")
        print(f"  2. Ver cursos: http://localhost:8000/cursos/")
        print(f"  3. Ver lecciones en los cursos")

if __name__ == "__main__":
    generador = GeneradorLeccionesCursos()
    generador.ejecutar()

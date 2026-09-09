#!/usr/bin/env python
"""
Generador automático de preguntas para Rhetorica Plus
Ejecuta: python generar_preguntas.py
"""

import os
import sys
import json
import random
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from core.models import EjercicioLinguistico, TecnicaLinguistica, Evaluacion
from django.contrib.auth.models import User
from django.db import connection

class Color:
    ROJO = '\033[91m'
    VERDE = '\033[92m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BLANCO = '\033[97m'
    NEGRITA = '\033[1m'
    FIN = '\033[0m'

class GeneradorPreguntas:
    def __init__(self):
        self.tipos_preguntas = [
            'correccion', 'completar', 'reescribir', 'elegir', 
            'explicar', 'verdadero_falso', 'relacionar', 'ordenar',
            'multiple_choice', 'desarrollo', 'analisis', 'sintesis'
        ]
        self.preguntas_generadas = []
        self.estadisticas = {}
        self.usuario_actual = None
        
    def generar_100_preguntas(self, usuario_id=None):
        """Generar 100 preguntas automáticas"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}📚 GENERADOR AUTOMÁTICO DE PREGUNTAS{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Obtener ejercicios base
        ejercicios_base = list(EjercicioLinguistico.objects.all())
        if len(ejercicios_base) < 100:
            print(f"{Color.AMARILLO}⚠️ Solo hay {len(ejercicios_base)} ejercicios base{Color.FIN}")
            print(f"{Color.AMARILLO}Generando con los disponibles...{Color.FIN}")
        
        # Generar preguntas por tipo
        preguntas_por_tipo = self._distribuir_preguntas()
        
        for tipo, cantidad in preguntas_por_tipo.items():
            print(f"\n{Color.MAGENTA}📌 Generando {cantidad} preguntas de tipo: {tipo}{Color.FIN}")
            for i in range(cantidad):
                pregunta = self._generar_pregunta_tipo(tipo, ejercicios_base)
                if pregunta:
                    self.preguntas_generadas.append(pregunta)
                    self.estadisticas[tipo] = self.estadisticas.get(tipo, 0) + 1
        
        print(f"\n{Color.VERDE}✅ Generadas {len(self.preguntas_generadas)} preguntas{Color.FIN}")
        return self.preguntas_generadas
    
    def _distribuir_preguntas(self):
        """Distribuir 100 preguntas entre los tipos"""
        return {
            'correccion': 20,
            'completar': 15,
            'reescribir': 15,
            'elegir': 10,
            'explicar': 10,
            'verdadero_falso': 10,
            'relacionar': 5,
            'ordenar': 5,
            'multiple_choice': 5,
            'desarrollo': 5,
        }
    
    def _generar_pregunta_tipo(self, tipo, ejercicios_base):
        """Generar pregunta de un tipo específico"""
        if not ejercicios_base:
            return None
        
        # Seleccionar ejercicio base aleatorio
        base = random.choice(ejercicios_base)
        contenido = base.contenido if isinstance(base.contenido, dict) else {}
        
        # Generar según tipo
        generadores = {
            'correccion': self._generar_correccion,
            'completar': self._generar_completar,
            'reescribir': self._generar_reescribir,
            'elegir': self._generar_elegir,
            'explicar': self._generar_explicar,
            'verdadero_falso': self._generar_vf,
            'relacionar': self._generar_relacionar,
            'ordenar': self._generar_ordenar,
            'multiple_choice': self._generar_multiple,
            'desarrollo': self._generar_desarrollo,
        }
        
        if tipo in generadores:
            return generadores[tipo](base, contenido)
        return None
    
    def _generar_correccion(self, base, contenido):
        """Generar pregunta de corrección"""
        if 'ejercicio' not in contenido:
            return None
        return {
            'tipo': 'correccion',
            'id': f"corr_{base.id}",
            'titulo': f"Corrige: {base.titulo}",
            'enunciado': contenido.get('ejercicio', ''),
            'respuesta_correcta': contenido.get('suggestedAnswer', ''),
            'pista': contenido.get('teoria', '')[:150],
            'dificultad': base.nivel or 1,
            'puntos': base.puntos or 10,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_completar(self, base, contenido):
        """Generar pregunta de completar"""
        if 'ejercicio' not in contenido:
            return None
        texto = contenido.get('ejercicio', '')
        # Extraer palabra faltante
        palabra_faltante = contenido.get('suggestedAnswer', '')
        if '___' in texto:
            enunciado = texto
        else:
            # Crear espacio en blanco
            palabras = texto.split()
            if len(palabras) > 3:
                idx = random.randint(1, len(palabras)-2)
                palabra_removida = palabras[idx]
                palabras[idx] = '___'
                enunciado = ' '.join(palabras)
                palabra_faltante = palabra_removida.strip('.,;:!?')
        
        return {
            'tipo': 'completar',
            'id': f"comp_{base.id}",
            'titulo': f"Completa: {base.titulo}",
            'enunciado': enunciado,
            'respuesta_correcta': palabra_faltante,
            'pista': contenido.get('teoria', '')[:150],
            'dificultad': base.nivel or 1,
            'puntos': base.puntos or 10,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_reescribir(self, base, contenido):
        """Generar pregunta de reescribir"""
        if 'ejemplo' not in contenido:
            return None
        ejemplo = contenido.get('ejemplo', '')
        return {
            'tipo': 'reescribir',
            'id': f"rees_{base.id}",
            'titulo': f"Reescribe: {base.titulo}",
            'enunciado': f"Reescribe la siguiente frase usando {contenido.get('name', 'la regla')}: '{ejemplo}'",
            'respuesta_correcta': contenido.get('suggestedAnswer', ejemplo),
            'pista': contenido.get('teoria', '')[:150],
            'dificultad': base.nivel or 1,
            'puntos': base.puntos or 10,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_elegir(self, base, contenido):
        """Generar pregunta de elegir"""
        if 'teoria' not in contenido:
            return None
        teoria = contenido.get('teoria', '')
        # Crear opciones basadas en la teoría
        opciones = [contenido.get('suggestedAnswer', 'Opción correcta')]
        palabras_clave = teoria.split()
        for _ in range(3):
            if len(palabras_clave) > 5:
                opcion = ' '.join(random.sample(palabras_clave, min(3, len(palabras_clave))))
                if opcion not in opciones and len(opcion) > 5:
                    opciones.append(opcion)
        random.shuffle(opciones)
        
        return {
            'tipo': 'elegir',
            'id': f"ele_{base.id}",
            'titulo': f"Elige: {base.titulo}",
            'enunciado': contenido.get('ejercicio', 'Elige la opción correcta'),
            'opciones': opciones[:4],
            'respuesta_correcta': opciones[0],
            'pista': teoria[:150],
            'dificultad': base.nivel or 1,
            'puntos': base.puntos or 10,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_explicar(self, base, contenido):
        """Generar pregunta de explicar"""
        if 'teoria' not in contenido:
            return None
        return {
            'tipo': 'explicar',
            'id': f"expl_{base.id}",
            'titulo': f"Explica: {base.titulo}",
            'enunciado': f"Explica con tus propias palabras: {contenido.get('name', 'el concepto')}",
            'respuesta_correcta': contenido.get('teoria', ''),
            'pista': f"Basado en: {contenido.get('name', 'el concepto')}",
            'dificultad': base.nivel or 1,
            'puntos': (base.puntos or 10) + 5,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_vf(self, base, contenido):
        """Generar pregunta de Verdadero/Falso"""
        if 'teoria' not in contenido:
            return None
        teoria = contenido.get('teoria', '')
        # Crear afirmación verdadera o falsa
        es_verdadero = random.choice([True, False])
        if es_verdadero:
            afirmacion = teoria[:100]
            respuesta = 'Verdadero'
        else:
            # Modificar la teoría para hacerla falsa
            palabras = teoria.split()
            if len(palabras) > 4:
                idx = random.randint(1, len(palabras)-1)
                palabras[idx] = 'no ' + palabras[idx] if not palabras[idx].startswith('no') else palabras[idx].replace('no ', '')
                afirmacion = ' '.join(palabras[:min(15, len(palabras))])
            else:
                afirmacion = teoria + ' (afirmación modificada)'
            respuesta = 'Falso'
        
        return {
            'tipo': 'verdadero_falso',
            'id': f"vf_{base.id}",
            'titulo': f"¿Verdadero o Falso? - {base.titulo}",
            'enunciado': f"¿Es correcta la siguiente afirmación?\n\n'{afirmacion}'",
            'respuesta_correcta': respuesta,
            'pista': f"Revisa: {contenido.get('name', 'el concepto')}",
            'dificultad': base.nivel or 1,
            'puntos': (base.puntos or 10) // 2,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_relacionar(self, base, contenido):
        """Generar pregunta de relacionar"""
        if 'teoria' not in contenido:
            return None
        conceptos = contenido.get('teoria', '').split('.')
        conceptos = [c.strip() for c in conceptos if len(c.strip()) > 20][:4]
        if len(conceptos) < 2:
            conceptos = ['Concepto 1', 'Concepto 2', 'Concepto 3', 'Concepto 4']
        
        return {
            'tipo': 'relacionar',
            'id': f"rel_{base.id}",
            'titulo': f"Relaciona conceptos: {base.titulo}",
            'enunciado': f"Relaciona cada concepto con su descripción correcta",
            'conceptos': [c[:30] + '...' for c in conceptos],
            'respuesta_correcta': ' | '.join([f"{i+1}->{chr(65+i)}" for i in range(len(conceptos))]),
            'pista': 'Relaciona según el contexto',
            'dificultad': (base.nivel or 1) + 1,
            'puntos': (base.puntos or 10) + 5,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_ordenar(self, base, contenido):
        """Generar pregunta de ordenar"""
        if 'teoria' not in contenido:
            return None
        pasos = [p.strip() for p in contenido.get('teoria', '').split('.') if len(p.strip()) > 10][:5]
        if len(pasos) < 3:
            pasos = ['Primer paso', 'Segundo paso', 'Tercer paso', 'Cuarto paso']
        
        orden_original = pasos.copy()
        random.shuffle(pasos)
        
        return {
            'tipo': 'ordenar',
            'id': f"ord_{base.id}",
            'titulo': f"Ordena correctamente: {base.titulo}",
            'enunciado': "Ordena los siguientes pasos de manera lógica",
            'pasos': pasos,
            'respuesta_correcta': ' | '.join(orden_original),
            'pista': 'Piensa en el orden lógico',
            'dificultad': (base.nivel or 1) + 1,
            'puntos': (base.puntos or 10) + 5,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_multiple(self, base, contenido):
        """Generar pregunta de opción múltiple"""
        if 'teoria' not in contenido:
            return None
        opciones = []
        # Opción correcta
        correcta = contenido.get('teoria', '')[:50]
        opciones.append(correcta)
        
        # Opciones incorrectas
        palabras = contenido.get('teoria', '').split()
        for _ in range(3):
            if len(palabras) > 10:
                opcion = ' '.join(random.sample(palabras, min(5, len(palabras))))
                if opcion not in opciones and len(opcion) > 10:
                    opciones.append(opcion)
        random.shuffle(opciones)
        
        return {
            'tipo': 'multiple_choice',
            'id': f"mult_{base.id}",
            'titulo': f"Selecciona la opción correcta: {base.titulo}",
            'enunciado': f"¿Cuál de las siguientes opciones es correcta según: {contenido.get('name', 'el concepto')}?",
            'opciones': opciones[:4],
            'respuesta_correcta': opciones[0],
            'pista': 'Revisa la teoría',
            'dificultad': (base.nivel or 1) + 1,
            'puntos': (base.puntos or 10) + 5,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_desarrollo(self, base, contenido):
        """Generar pregunta de desarrollo"""
        if 'teoria' not in contenido:
            return None
        return {
            'tipo': 'desarrollo',
            'id': f"des_{base.id}",
            'titulo': f"Desarrolla el tema: {base.titulo}",
            'enunciado': f"Desarrolla un texto explicativo sobre: {contenido.get('name', 'el tema')}",
            'respuesta_correcta': contenido.get('teoria', ''),
            'pista': 'Incluye definición, características y ejemplos',
            'dificultad': (base.nivel or 1) + 2,
            'puntos': (base.puntos or 10) + 10,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def guardar_preguntas(self, usuario=None):
        """Guardar preguntas generadas en archivos"""
        fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Guardar todos los tipos
        with open(f'preguntas_generadas_{fecha}.json', 'w', encoding='utf-8') as f:
            json.dump({
                'fecha': fecha,
                'total': len(self.preguntas_generadas),
                'estadisticas': self.estadisticas,
                'preguntas': self.preguntas_generadas
            }, f, ensure_ascii=False, indent=2)
        
        # Guardar por tipo
        for tipo in self.estadisticas:
            preguntas_tipo = [p for p in self.preguntas_generadas if p['tipo'] == tipo]
            if preguntas_tipo:
                with open(f'preguntas_{tipo}_{fecha}.json', 'w', encoding='utf-8') as f:
                    json.dump(preguntas_tipo, f, ensure_ascii=False, indent=2)
        
        print(f"\n{Color.VERDE}✅ Preguntas guardadas en archivos JSON{Color.FIN}")
        return fecha

# Dashboard para profesor
class DashboardProfesor:
    @staticmethod
    def mostrar_estadisticas():
        """Mostrar estadísticas del dashboard del profesor"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}👨‍🏫 DASHBOARD DEL PROFESOR{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        
        print(f"\n📊 ESTADÍSTICAS GENERALES:")
        print(f"  Total ejercicios: {EjercicioLinguistico.objects.count()}")
        print(f"  Total técnicas: {TecnicaLinguistica.objects.count()}")
        print(f"  Total usuarios: {User.objects.count()}")
        
        # Tipos de preguntas
        tipos = {}
        for e in EjercicioLinguistico.objects.all()[:100]:
            contenido = e.contenido
            if isinstance(contenido, dict) and 'ejercicio' in contenido:
                texto = contenido['ejercicio'].lower()
                if 'corrige' in texto:
                    tipos['correccion'] = tipos.get('correccion', 0) + 1
                elif 'completa' in texto:
                    tipos['completar'] = tipos.get('completar', 0) + 1
                elif 'reemplaza' in texto:
                    tipos['reescribir'] = tipos.get('reescribir', 0) + 1
                elif 'elige' in texto:
                    tipos['elegir'] = tipos.get('elegir', 0) + 1
                else:
                    tipos['otros'] = tipos.get('otros', 0) + 1
        
        print(f"\n📝 TIPOS DE PREGUNTAS:")
        for tipo, cantidad in tipos.items():
            print(f"  {tipo}: {cantidad}")
    
    @staticmethod
    def generar_prueba(cantidad=10):
        """Generar prueba personalizada para profesor"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}📝 GENERAR PRUEBA PERSONALIZADA{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        
        generador = GeneradorPreguntas()
        preguntas = generador.generar_100_preguntas()
        
        # Seleccionar aleatoriamente
        seleccionadas = random.sample(preguntas, min(cantidad, len(preguntas)))
        
        print(f"\n📋 PRUEBA DE {len(seleccionadas)} PREGUNTAS:")
        for i, p in enumerate(seleccionadas, 1):
            print(f"\n{i}. {p['titulo']}")
            print(f"   Tipo: {p['tipo']}")
            print(f"   Dificultad: {p.get('dificultad', 1)}")
            print(f"   Puntos: {p.get('puntos', 10)}")
            print(f"   Enunciado: {p['enunciado'][:100]}...")
        
        return seleccionadas

# Dashboard para estudiante
class DashboardEstudiante:
    @staticmethod
    def practicar_aleatorio(cantidad=5):
        """Generar práctica aleatoria para estudiante"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}🎯 PRÁCTICA PARA ESTUDIANTE{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        
        # Obtener ejercicios aleatorios
        ejercicios = list(EjercicioLinguistico.objects.all())
        seleccionados = random.sample(ejercicios, min(cantidad, len(ejercicios)))
        
        print(f"\n📖 PRÁCTICA DE {len(seleccionados)} EJERCICIOS:")
        for i, e in enumerate(seleccionados, 1):
            contenido = e.contenido if isinstance(e.contenido, dict) else {}
            print(f"\n{i}. {e.titulo}")
            print(f"   Categoría: {e.categoria}")
            print(f"   Nivel: {e.nivel}")
            print(f"   Puntos: {e.puntos}")
            if 'ejercicio' in contenido:
                print(f"   Ejercicio: {contenido['ejercicio'][:100]}...")
            if 'suggestedAnswer' in contenido:
                print(f"   💡 Pista: {contenido['suggestedAnswer'][:50]}...")
        
        return seleccionados

# Dashboard para admin
class DashboardAdmin:
    @staticmethod
    def estadisticas_avanzadas():
        """Estadísticas avanzadas para admin"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}👑 DASHBOARD DEL ADMINISTRADOR{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        
        # Estadísticas de base de datos
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
            total_tablas = cursor.fetchone()[0]
        
        print(f"\n📊 ESTADÍSTICAS DEL SISTEMA:")
        print(f"  Total tablas: {total_tablas}")
        print(f"  Total ejercicios: {EjercicioLinguistico.objects.count()}")
        print(f"  Total usuarios: {User.objects.count()}")
        
        # Últimos usuarios
        print(f"\n👥 ÚLTIMOS USUARIOS:")
        for user in User.objects.all().order_by('-date_joined')[:5]:
            print(f"  {user.username} - {user.email} ({user.date_joined.strftime('%Y-%m-%d')})")
        
        # Distribución de ejercicios por categoría
        print(f"\n📂 DISTRIBUCIÓN POR CATEGORÍA:")
        categorias = {}
        for e in EjercicioLinguistico.objects.all():
            categorias[e.categoria] = categorias.get(e.categoria, 0) + 1
        for cat, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {cat}: {count} ejercicios")

# Función principal
def main():
    print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
    print(f"{Color.NEGRITA}🚀 GENERADOR AUTOMÁTICO DE PREGUNTAS - RHETORICA PLUS{Color.FIN}")
    print(f"{Color.CYAN}{'='*70}{Color.FIN}")
    
    menu = f"""
{Color.AMARILLO}Selecciona una opción:{Color.FIN}
1. 👨‍🏫 Dashboard del Profesor
2. 🎯 Dashboard del Estudiante  
3. 👑 Dashboard del Admin
4. 📚 Generar 100 preguntas automáticas
5. 📝 Generar prueba personalizada (profesor)
6. 🎲 Práctica aleatoria (estudiante)
7. 📊 Ver estadísticas generales
8. 💾 Guardar preguntas en archivos
9. 🔄 Ver 5 tipos de preguntas
0. ❌ Salir
"""
    
    while True:
        print(menu)
        opcion = input(f"\n{Color.CYAN}Opción: {Color.FIN}")
        
        if opcion == '0':
            print(f"\n{Color.VERDE}👋 ¡Hasta luego!{Color.FIN}")
            break
        
        elif opcion == '1':
            DashboardProfesor.mostrar_estadisticas()
        
        elif opcion == '2':
            preguntas = DashboardEstudiante.practicar_aleatorio(5)
        
        elif opcion == '3':
            DashboardAdmin.estadisticas_avanzadas()
        
        elif opcion == '4':
            generador = GeneradorPreguntas()
            preguntas = generador.generar_100_preguntas()
            if preguntas:
                print(f"\n{Color.VERDE}✅ Generadas {len(preguntas)} preguntas{Color.FIN}")
        
        elif opcion == '5':
            cantidad = input("¿Cuántas preguntas para la prueba? (default 10): ")
            try:
                cantidad = int(cantidad) if cantidad else 10
            except:
                cantidad = 10
            DashboardProfesor.generar_prueba(cantidad)
        
        elif opcion == '6':
            cantidad = input("¿Cuántos ejercicios para practicar? (default 5): ")
            try:
                cantidad = int(cantidad) if cantidad else 5
            except:
                cantidad = 5
            DashboardEstudiante.practicar_aleatorio(cantidad)
        
        elif opcion == '7':
            generador = GeneradorPreguntas()
            generador.generar_100_preguntas()
            print(f"\n{Color.VERDE}📊 Estadísticas:{Color.FIN}")
            for tipo, cantidad in generador.estadisticas.items():
                print(f"  {tipo}: {cantidad} preguntas")
        
        elif opcion == '8':
            generador = GeneradorPreguntas()
            preguntas = generador.generar_100_preguntas()
            fecha = generador.guardar_preguntas()
            print(f"\n{Color.VERDE}✅ Archivos guardados con fecha: {fecha}{Color.FIN}")
        
        elif opcion == '9':
            print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
            print(f"{Color.NEGRITA}📖 5 TIPOS DE PREGUNTAS EJEMPLO{Color.FIN}")
            print(f"{Color.CYAN}{'='*70}{Color.FIN}")
            
            generador = GeneradorPreguntas()
            ejercicios_base = list(EjercicioLinguistico.objects.all())
            
            tipos_ejemplo = ['correccion', 'completar', 'reescribir', 'elegir', 'explicar']
            for i, tipo in enumerate(tipos_ejemplo, 1):
                for base in ejercicios_base:
                    contenido = base.contenido if isinstance(base.contenido, dict) else {}
                    if tipo == 'correccion' and 'corrige' in contenido.get('ejercicio', '').lower():
                        pregunta = generador._generar_correccion(base, contenido)
                        break
                    elif tipo == 'completar' and 'completa' in contenido.get('ejercicio', '').lower():
                        pregunta = generador._generar_completar(base, contenido)
                        break
                    elif tipo == 'reescribir' and 'reemplaza' in contenido.get('ejercicio', '').lower():
                        pregunta = generador._generar_reescribir(base, contenido)
                        break
                    elif tipo == 'elegir' and 'elige' in contenido.get('ejercicio', '').lower():
                        pregunta = generador._generar_elegir(base, contenido)
                        break
                    elif tipo == 'explicar':
                        pregunta = generador._generar_explicar(base, contenido)
                        break
                else:
                    continue
                
                if pregunta:
                    print(f"\n{Color.MAGENTA}{i}. {tipo.upper()}{Color.FIN}")
                    print(f"   {pregunta['titulo']}")
                    print(f"   Enunciado: {pregunta['enunciado'][:100]}...")
                    print(f"   Respuesta: {pregunta['respuesta_correcta'][:80]}...")
        
        else:
            print(f"{Color.ROJO}❌ Opción no válida{Color.FIN}")
        
        input(f"\n{Color.AMARILLO}Presiona Enter para continuar...{Color.FIN}")

if __name__ == "__main__":
    main()

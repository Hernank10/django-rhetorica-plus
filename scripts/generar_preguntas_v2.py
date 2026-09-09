#!/usr/bin/env python
"""
Generador automático de preguntas para Rhetorica Plus (Versión Corregida)
Ejecuta: python generar_preguntas_v2.py
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

from core.models import EjercicioLinguistico, TecnicaLinguistica
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
            'multiple_choice', 'desarrollo'
        ]
        self.preguntas_generadas = []
        self.estadisticas = {}
        
    def generar_100_preguntas(self):
        """Generar 100 preguntas automáticas"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}📚 GENERADOR AUTOMÁTICO DE PREGUNTAS{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        ejercicios_base = list(EjercicioLinguistico.objects.all())
        if len(ejercicios_base) < 100:
            print(f"{Color.AMARILLO}⚠️ Solo hay {len(ejercicios_base)} ejercicios base{Color.FIN}")
        
        # Distribuir preguntas
        distribucion = {
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
        
        for tipo, cantidad in distribucion.items():
            print(f"\n{Color.MAGENTA}📌 Generando {cantidad} preguntas de tipo: {tipo}{Color.FIN}")
            for i in range(cantidad):
                if ejercicios_base:
                    base = random.choice(ejercicios_base)
                    contenido = base.contenido if isinstance(base.contenido, dict) else {}
                    pregunta = self._generar_pregunta_segura(tipo, base, contenido)
                    if pregunta:
                        self.preguntas_generadas.append(pregunta)
                        self.estadisticas[tipo] = self.estadisticas.get(tipo, 0) + 1
        
        print(f"\n{Color.VERDE}✅ Generadas {len(self.preguntas_generadas)} preguntas{Color.FIN}")
        return self.preguntas_generadas
    
    def _generar_pregunta_segura(self, tipo, base, contenido):
        """Generar pregunta con manejo de errores"""
        try:
            if tipo == 'correccion':
                return self._generar_correccion(base, contenido)
            elif tipo == 'completar':
                return self._generar_completar(base, contenido)
            elif tipo == 'reescribir':
                return self._generar_reescribir(base, contenido)
            elif tipo == 'elegir':
                return self._generar_elegir(base, contenido)
            elif tipo == 'explicar':
                return self._generar_explicar(base, contenido)
            elif tipo == 'verdadero_falso':
                return self._generar_vf(base, contenido)
            elif tipo == 'relacionar':
                return self._generar_relacionar(base, contenido)
            elif tipo == 'ordenar':
                return self._generar_ordenar(base, contenido)
            elif tipo == 'multiple_choice':
                return self._generar_multiple(base, contenido)
            elif tipo == 'desarrollo':
                return self._generar_desarrollo(base, contenido)
        except Exception as e:
            return None
    
    def _generar_correccion(self, base, contenido):
        """Generar pregunta de corrección"""
        ejercicio = contenido.get('ejercicio', '')
        if not ejercicio:
            return None
            
        return {
            'tipo': 'correccion',
            'id': f"corr_{base.id}",
            'titulo': f"Corrige: {base.titulo}",
            'enunciado': ejercicio,
            'respuesta_correcta': contenido.get('suggestedAnswer', 'Revisa la teoría'),
            'pista': contenido.get('teoria', '')[:150],
            'dificultad': base.nivel or 1,
            'puntos': base.puntos or 10,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_completar(self, base, contenido):
        """Generar pregunta de completar"""
        ejercicio = contenido.get('ejercicio', '')
        respuesta = contenido.get('suggestedAnswer', '')
        
        if not ejercicio:
            return None
        
        # Si tiene ___, usarlo; si no, crear un espacio
        if '___' in ejercicio:
            enunciado = ejercicio
            respuesta = respuesta if respuesta else 'palabra_faltante'
        else:
            # Crear espacio en blanco
            palabras = ejercicio.split()
            if len(palabras) > 3:
                idx = random.randint(1, len(palabras)-2)
                palabra_removida = palabras[idx]
                palabras[idx] = '___'
                enunciado = ' '.join(palabras)
                respuesta = palabra_removida.strip('.,;:!?')
            else:
                enunciado = ejercicio + " ___"
                respuesta = respuesta if respuesta else 'palabra_faltante'
        
        return {
            'tipo': 'completar',
            'id': f"comp_{base.id}",
            'titulo': f"Completa: {base.titulo}",
            'enunciado': enunciado,
            'respuesta_correcta': respuesta,
            'pista': contenido.get('teoria', '')[:150],
            'dificultad': base.nivel or 1,
            'puntos': base.puntos or 10,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_reescribir(self, base, contenido):
        """Generar pregunta de reescribir"""
        ejemplo = contenido.get('ejemplo', '')
        if not ejemplo:
            ejemplo = contenido.get('teoria', '')[:100]
        
        return {
            'tipo': 'reescribir',
            'id': f"rees_{base.id}",
            'titulo': f"Reescribe: {base.titulo}",
            'enunciado': f"Reescribe la siguiente frase usando la regla: '{ejemplo}'",
            'respuesta_correcta': contenido.get('suggestedAnswer', ejemplo),
            'pista': contenido.get('teoria', '')[:150],
            'dificultad': base.nivel or 1,
            'puntos': base.puntos or 10,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_elegir(self, base, contenido):
        """Generar pregunta de elegir"""
        teoria = contenido.get('teoria', '')
        if not teoria:
            return None
            
        respuesta = contenido.get('suggestedAnswer', 'Opción correcta')
        opciones = [respuesta]
        
        # Crear opciones falsas
        palabras = teoria.split()
        for _ in range(3):
            if len(palabras) > 5:
                opcion = ' '.join(random.sample(palabras, min(3, len(palabras))))
                if opcion not in opciones and len(opcion) > 3:
                    opciones.append(opcion)
        
        random.shuffle(opciones)
        
        return {
            'tipo': 'elegir',
            'id': f"ele_{base.id}",
            'titulo': f"Elige: {base.titulo}",
            'enunciado': contenido.get('ejercicio', 'Elige la opción correcta'),
            'opciones': opciones[:4],
            'respuesta_correcta': respuesta,
            'pista': teoria[:150],
            'dificultad': base.nivel or 1,
            'puntos': base.puntos or 10,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_explicar(self, base, contenido):
        """Generar pregunta de explicar"""
        nombre = contenido.get('name', 'el concepto')
        return {
            'tipo': 'explicar',
            'id': f"expl_{base.id}",
            'titulo': f"Explica: {base.titulo}",
            'enunciado': f"Explica con tus propias palabras: {nombre}",
            'respuesta_correcta': contenido.get('teoria', ''),
            'pista': f"Basado en: {nombre}",
            'dificultad': (base.nivel or 1) + 1,
            'puntos': (base.puntos or 10) + 5,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_vf(self, base, contenido):
        """Generar pregunta de Verdadero/Falso"""
        teoria = contenido.get('teoria', '')
        if not teoria:
            return None
            
        es_verdadero = random.choice([True, False])
        if es_verdadero:
            afirmacion = teoria[:100]
            respuesta = 'Verdadero'
        else:
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
        teoria = contenido.get('teoria', '')
        conceptos = [c.strip() for c in teoria.split('.') if len(c.strip()) > 15][:4]
        if len(conceptos) < 2:
            conceptos = ['Concepto 1', 'Concepto 2', 'Concepto 3', 'Concepto 4']
        
        return {
            'tipo': 'relacionar',
            'id': f"rel_{base.id}",
            'titulo': f"Relaciona conceptos: {base.titulo}",
            'enunciado': "Relaciona cada concepto con su descripción correcta",
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
        teoria = contenido.get('teoria', '')
        pasos = [p.strip() for p in teoria.split('.') if len(p.strip()) > 10][:5]
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
        teoria = contenido.get('teoria', '')
        if not teoria:
            return None
            
        respuesta = contenido.get('suggestedAnswer', teoria[:50])
        opciones = [respuesta]
        
        palabras = teoria.split()
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
            'enunciado': f"¿Cuál de las siguientes opciones es correcta?",
            'opciones': opciones[:4],
            'respuesta_correcta': respuesta,
            'pista': 'Revisa la teoría',
            'dificultad': (base.nivel or 1) + 1,
            'puntos': (base.puntos or 10) + 5,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def _generar_desarrollo(self, base, contenido):
        """Generar pregunta de desarrollo"""
        nombre = contenido.get('name', 'el tema')
        return {
            'tipo': 'desarrollo',
            'id': f"des_{base.id}",
            'titulo': f"Desarrolla el tema: {base.titulo}",
            'enunciado': f"Desarrolla un texto explicativo sobre: {nombre}",
            'respuesta_correcta': contenido.get('teoria', ''),
            'pista': 'Incluye definición, características y ejemplos',
            'dificultad': (base.nivel or 1) + 2,
            'puntos': (base.puntos or 10) + 10,
            'categoria': base.categoria,
            'ejercicio_base_id': base.id
        }
    
    def guardar_preguntas(self):
        """Guardar preguntas generadas"""
        fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with open(f'preguntas_generadas_{fecha}.json', 'w', encoding='utf-8') as f:
            json.dump({
                'fecha': fecha,
                'total': len(self.preguntas_generadas),
                'estadisticas': self.estadisticas,
                'preguntas': self.preguntas_generadas
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n{Color.VERDE}✅ Preguntas guardadas en preguntas_generadas_{fecha}.json{Color.FIN}")
        return fecha

def main():
    print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
    print(f"{Color.NEGRITA}🚀 GENERADOR AUTOMÁTICO DE PREGUNTAS - RHETORICA PLUS{Color.FIN}")
    print(f"{Color.CYAN}{'='*70}{Color.FIN}")
    
    generador = GeneradorPreguntas()
    
    while True:
        print(f"""
{Color.AMARILLO}Selecciona una opción:{Color.FIN}
1. 📚 Generar 100 preguntas automáticas
2. 💾 Guardar preguntas en archivos
3. 📊 Ver estadísticas
4. 🔄 Ver muestra de 5 tipos
0. ❌ Salir
""")
        
        opcion = input(f"{Color.CYAN}Opción: {Color.FIN}")
        
        if opcion == '0':
            print(f"\n{Color.VERDE}👋 ¡Hasta luego!{Color.FIN}")
            break
        elif opcion == '1':
            generador.preguntas_generadas = []
            generador.estadisticas = {}
            preguntas = generador.generar_100_preguntas()
            if preguntas:
                print(f"\n{Color.VERDE}✅ Generadas {len(preguntas)} preguntas{Color.FIN}")
                for tipo, count in generador.estadisticas.items():
                    print(f"  {tipo}: {count}")
        elif opcion == '2':
            if generador.preguntas_generadas:
                generador.guardar_preguntas()
            else:
                print(f"{Color.AMARILLO}⚠️ Primero genera preguntas (opción 1){Color.FIN}")
        elif opcion == '3':
            print(f"\n{Color.NEGRITA}📊 ESTADÍSTICAS:{Color.FIN}")
            if generador.estadisticas:
                for tipo, count in generador.estadisticas.items():
                    print(f"  {tipo}: {count} preguntas")
            else:
                print("  No hay preguntas generadas")
        elif opcion == '4':
            print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
            print(f"{Color.NEGRITA}📖 MUESTRA DE 5 TIPOS DE PREGUNTAS{Color.FIN}")
            print(f"{Color.CYAN}{'='*70}{Color.FIN}")
            
            generador.preguntas_generadas = []
            generador.estadisticas = {}
            generador.generar_100_preguntas()
            
            for i, tipo in enumerate(['correccion', 'completar', 'reescribir', 'elegir', 'explicar'], 1):
                preguntas_tipo = [p for p in generador.preguntas_generadas if p['tipo'] == tipo]
                if preguntas_tipo:
                    p = preguntas_tipo[0]
                    print(f"\n{Color.MAGENTA}{i}. {tipo.upper()}{Color.FIN}")
                    print(f"   {p['titulo']}")
                    print(f"   Enunciado: {p['enunciado'][:100]}...")
                    print(f"   Respuesta: {p['respuesta_correcta'][:80]}...")
        else:
            print(f"{Color.ROJO}❌ Opción no válida{Color.FIN}")
        
        input(f"\n{Color.AMARILLO}Presiona Enter para continuar...{Color.FIN}")

if __name__ == "__main__":
    main()

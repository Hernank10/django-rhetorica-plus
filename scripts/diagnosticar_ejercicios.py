#!/usr/bin/env python
"""Script de diagnóstico y corrección de ejercicios"""

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
from django.db import connection
from django.contrib.auth.models import User

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

class DiagnosticadorEjercicios:
    def __init__(self):
        self.errores = []
        self.correcciones = []
        self.total_ejercicios = 0
        self.ejercicios_validos = 0
        self.ejercicios_con_error = 0
        
    def diagnosticar(self):
        """Ejecutar diagnóstico completo"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}🔍 DIAGNÓSTICO DE EJERCICIOS - RHETORICA PLUS{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 1. Verificar base de datos
        self._verificar_bd()
        
        # 2. Verificar estructura de ejercicios
        self._verificar_estructura()
        
        # 3. Verificar tipos de preguntas
        self._verificar_tipos_preguntas()
        
        # 4. Generar muestra de 5 tipos de preguntas
        self._generar_muestra()
        
        # 5. Verificar contenido
        self._verificar_contenido()
        
        # 6. Resumen final
        self._resumen_final()
        
    def _verificar_bd(self):
        """Verificar conexión y estadísticas básicas"""
        print(f"{Color.NEGRITA}📊 1. ESTADO DE LA BASE DE DATOS{Color.FIN}")
        print("-" * 50)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM core_ejerciciolinguistico")
                self.total_ejercicios = cursor.fetchone()[0]
                print(f"{Color.VERDE}✅ Total ejercicios: {self.total_ejercicios}{Color.FIN}")
        except Exception as e:
            print(f"{Color.ROJO}❌ Error en BD: {e}{Color.FIN}")
            self.errores.append(f"Error BD: {e}")
    
    def _verificar_estructura(self):
        """Verificar estructura de los ejercicios"""
        print(f"\n{Color.NEGRITA}📋 2. ESTRUCTURA DE EJERCICIOS{Color.FIN}")
        print("-" * 50)
        
        ejercicios = EjercicioLinguistico.objects.all()[:100]
        
        campos_requeridos = ['id', 'name', 'teoria', 'ejemplo', 'ejercicio', 'suggestedAnswer']
        
        for ejercicio in ejercicios:
            contenido = ejercicio.contenido
            if isinstance(contenido, dict):
                # Verificar campos requeridos
                faltantes = [campo for campo in campos_requeridos if campo not in contenido]
                if faltantes:
                    self.ejercicios_con_error += 1
                    self.errores.append(f"ID {ejercicio.id}: Faltan campos {faltantes}")
                else:
                    self.ejercicios_validos += 1
            else:
                self.ejercicios_con_error += 1
                self.errores.append(f"ID {ejercicio.id}: Contenido no es diccionario")
        
        print(f"{Color.VERDE}✅ Válidos: {self.ejercicios_validos}{Color.FIN}")
        if self.ejercicios_con_error > 0:
            print(f"{Color.AMARILLO}⚠️ Con errores: {self.ejercicios_con_error}{Color.FIN}")
    
    def _verificar_tipos_preguntas(self):
        """Identificar tipos de preguntas"""
        print(f"\n{Color.NEGRITA}🎯 3. TIPOS DE PREGUNTAS DETECTADOS{Color.FIN}")
        print("-" * 50)
        
        tipos = {
            'correccion': 0,
            'completar': 0,
            'reescribir': 0,
            'elegir': 0,
            'explicar': 0,
            'otros': 0
        }
        
        palabras_clave = {
            'correccion': ['corrige', 'corrige:', 'error', 'incorrecto'],
            'completar': ['completa', 'completa:', 'rellena', '___'],
            'reescribir': ['reemplaza', 'reescribe', 'sustituye', 'convierte'],
            'elegir': ['elige', 'selecciona', 'cuál', 'qué opción'],
            'explicar': ['explica', 'define', 'describe', '¿por qué']
        }
        
        for ejercicio in EjercicioLinguistico.objects.all()[:100]:
            contenido = ejercicio.contenido
            if isinstance(contenido, dict) and 'ejercicio' in contenido:
                texto = contenido['ejercicio'].lower()
                tipo_encontrado = False
                for tipo, palabras in palabras_clave.items():
                    if any(palabra in texto for palabra in palabras):
                        tipos[tipo] += 1
                        tipo_encontrado = True
                        break
                if not tipo_encontrado:
                    tipos['otros'] += 1
        
        for tipo, cantidad in tipos.items():
            if cantidad > 0:
                emoji = {
                    'correccion': '✏️', 'completar': '📝', 
                    'reescribir': '🔄', 'elegir': '✅', 
                    'explicar': '💡', 'otros': '📌'
                }[tipo]
                print(f"{emoji} {tipo.capitalize()}: {cantidad} ejercicios")
    
    def _generar_muestra(self):
        """Generar muestra de 5 tipos de preguntas"""
        print(f"\n{Color.NEGRITA}📖 4. MUESTRA DE 5 TIPOS DE PREGUNTAS{Color.FIN}")
        print("-" * 50)
        
        # Buscar ejercicios de diferentes tipos
        ejercicios_muestra = []
        tipos_buscados = ['correccion', 'completar', 'reescribir', 'elegir', 'explicar']
        
        for tipo in tipos_buscados:
            encontrado = False
            for ejercicio in EjercicioLinguistico.objects.all():
                contenido = ejercicio.contenido
                if isinstance(contenido, dict) and 'ejercicio' in contenido:
                    texto = contenido['ejercicio'].lower()
                    if tipo == 'correccion' and any(p in texto for p in ['corrige', 'error']):
                        ejercicios_muestra.append((tipo, ejercicio))
                        encontrado = True
                        break
                    elif tipo == 'completar' and ('completa' in texto or '___' in texto):
                        ejercicios_muestra.append((tipo, ejercicio))
                        encontrado = True
                        break
                    elif tipo == 'reescribir' and any(p in texto for p in ['reemplaza', 'reescribe']):
                        ejercicios_muestra.append((tipo, ejercicio))
                        encontrado = True
                        break
                    elif tipo == 'elegir' and any(p in texto for p in ['elige', 'selecciona']):
                        ejercicios_muestra.append((tipo, ejercicio))
                        encontrado = True
                        break
                    elif tipo == 'explicar' and any(p in texto for p in ['explica', 'define']):
                        ejercicios_muestra.append((tipo, ejercicio))
                        encontrado = True
                        break
            
            if not encontrado:
                # Si no encuentra, tomar cualquier ejercicio
                for ejercicio in EjercicioLinguistico.objects.all():
                    if ejercicio not in [e[1] for e in ejercicios_muestra]:
                        ejercicios_muestra.append((tipo, ejercicio))
                        break
        
        # Mostrar muestra
        for i, (tipo, ejercicio) in enumerate(ejercicios_muestra[:5], 1):
            contenido = ejercicio.contenido
            print(f"\n{Color.MAGENTA}📌 Ejemplo {i}: {tipo.upper()}{Color.FIN}")
            print(f"   ID: {ejercicio.id} - {ejercicio.titulo}")
            print(f"   {Color.CYAN}Teoría:{Color.FIN} {contenido.get('teoria', '')[:100]}...")
            print(f"   {Color.AMARILLO}Ejercicio:{Color.FIN} {contenido.get('ejercicio', '')[:150]}...")
            print(f"   {Color.VERDE}Respuesta sugerida:{Color.FIN} {contenido.get('suggestedAnswer', '')[:100]}...")
    
    def _verificar_contenido(self):
        """Verificar calidad del contenido"""
        print(f"\n{Color.NEGRITA}🔍 5. VERIFICACIÓN DE CONTENIDO{Color.FIN}")
        print("-" * 50)
        
        problemas = []
        
        for ejercicio in EjercicioLinguistico.objects.all()[:50]:
            contenido = ejercicio.contenido
            if isinstance(contenido, dict):
                # Verificar campos vacíos
                for campo in ['teoria', 'ejercicio']:
                    if campo in contenido and len(str(contenido[campo])) < 5:
                        problemas.append(f"ID {ejercicio.id}: Campo '{campo}' muy corto")
                
                # Verificar respuesta sugerida
                if 'suggestedAnswer' not in contenido or len(str(contenido.get('suggestedAnswer', ''))) < 2:
                    problemas.append(f"ID {ejercicio.id}: Sin respuesta sugerida")
        
        if problemas:
            print(f"{Color.AMARILLO}⚠️ {len(problemas)} problemas detectados (mostrando primeros 5):{Color.FIN}")
            for p in problemas[:5]:
                print(f"   - {p}")
        else:
            print(f"{Color.VERDE}✅ Contenido verificado sin problemas{Color.FIN}")
    
    def _resumen_final(self):
        """Mostrar resumen final"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}📊 RESUMEN FINAL{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        
        print(f"\n{Color.VERDE}✅ Total ejercicios: {self.total_ejercicios}{Color.FIN}")
        print(f"{Color.VERDE}✅ Ejercicios válidos: {self.ejercicios_validos}{Color.FIN}")
        if self.ejercicios_con_error > 0:
            print(f"{Color.AMARILLO}⚠️ Con errores: {self.ejercicios_con_error}{Color.FIN}")
        
        if self.errores:
            print(f"\n{Color.AMARILLO}⚠️ Errores encontrados:{Color.FIN}")
            for error in self.errores[:5]:
                print(f"   - {error}")
            if len(self.errores) > 5:
                print(f"   ... y {len(self.errores) - 5} más")
        else:
            print(f"\n{Color.VERDE}🎉 ¡No se encontraron errores!{Color.FIN}")
        
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}💡 RECOMENDACIONES:{Color.FIN}")
        print("1. Los ejercicios tienen buena estructura general")
        print("2. Verificar que todos tengan 'suggestedAnswer'")
        print("3. Asegurar que 'ejercicio' esté completo")
        print("4. Revisar que 'teoria' sea explicativa")
        print("5. Considerar agregar más categorías específicas")

# Script de corrección automática
class CorrectorEjercicios:
    def __init__(self):
        self.corregidos = 0
        self.errores = []
    
    def corregir(self):
        """Corregir ejercicios con problemas"""
        print(f"\n{Color.CYAN}{'='*70}{Color.FIN}")
        print(f"{Color.NEGRITA}🛠️ CORRECCIÓN AUTOMÁTICA{Color.FIN}")
        print(f"{Color.CYAN}{'='*70}{Color.FIN}")
        
        for ejercicio in EjercicioLinguistico.objects.all():
            contenido = ejercicio.contenido
            if isinstance(contenido, dict):
                modificado = False
                
                # Asegurar campos requeridos
                if 'suggestedAnswer' not in contenido:
                    contenido['suggestedAnswer'] = 'Respuesta sugerida no disponible'
                    modificado = True
                
                if 'ejemplo' not in contenido:
                    contenido['ejemplo'] = 'Ejemplo no disponible'
                    modificado = True
                
                if modificado:
                    ejercicio.contenido = contenido
                    ejercicio.save()
                    self.corregidos += 1
        
        print(f"{Color.VERDE}✅ Ejercicios corregidos: {self.corregidos}{Color.FIN}")

# Ejecutar
if __name__ == "__main__":
    # Diagnóstico
    diag = DiagnosticadorEjercicios()
    diag.diagnosticar()
    
    # Preguntar si corregir
    print(f"\n{Color.AMARILLO}¿Deseas ejecutar corrección automática? (s/n){Color.FIN}")
    respuesta = input("> ")
    if respuesta.lower() == 's':
        corrector = CorrectorEjercicios()
        corrector.corregir()
    
    print(f"\n{Color.VERDE}✅ Diagnóstico completado{Color.FIN}")

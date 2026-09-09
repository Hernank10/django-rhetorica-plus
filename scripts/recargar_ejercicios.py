#!/usr/bin/env python
"""
Script para limpiar y recargar ejercicios desde archivo JSON
Ejecuta: python recargar_ejercicios.py
"""

import os
import sys
import json
import glob
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from core.models import EjercicioLinguistico, TecnicaLinguistica
from django.db import transaction

class Color:
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    NEGRITA = '\033[1m'
    FIN = '\033[0m'

class RecargadorEjercicios:
    def __init__(self):
        self.archivo_json = None
        self.ejercicios_cargados = 0
        self.ejercicios_con_error = 0
        self.tecnicas_creadas = 0
        
    def buscar_archivo_json(self):
        """Buscar el archivo JSON con los ejercicios"""
        archivos = glob.glob('*.json')
        # Buscar archivos que parezcan tener ejercicios
        posibles = [f for f in archivos if 'ejercicio' in f.lower() or 'item' in f.lower() or 'data' in f.lower()]
        
        if posibles:
            print(f"{Color.AZUL}📂 Archivos JSON encontrados:{Color.FIN}")
            for i, archivo in enumerate(posibles, 1):
                print(f"  {i}. {archivo}")
            
            if len(posibles) == 1:
                self.archivo_json = posibles[0]
                print(f"\n{Color.VERDE}✅ Usando: {self.archivo_json}{Color.FIN}")
                return True
            else:
                try:
                    opcion = int(input(f"\n{Color.AMARILLO}Selecciona el archivo (1-{len(posibles)}): {Color.FIN}"))
                    if 1 <= opcion <= len(posibles):
                        self.archivo_json = posibles[opcion-1]
                        return True
                except:
                    pass
        
        # Si no hay archivo, crear uno desde los datos incluidos
        print(f"{Color.AMARILLO}⚠️ No se encontró archivo JSON. Creando uno de prueba...{Color.FIN}")
        self._crear_json_ejemplo()
        return True
    
    def _crear_json_ejemplo(self):
        """Crear un archivo JSON de ejemplo con algunos ejercicios"""
        datos_ejemplo = [
            {
                "id": 5085,
                "titulo": "Item 100",
                "categoria": "Gramatica",
                "tipo": "General",
                "nivel": 1,
                "puntos": 10,
                "contenido": {
                    "id": 100,
                    "name": "Uso de 'acorde' como adjetivo invariable",
                    "category": "Adjetivos",
                    "teoria": "'Acorde' significa 'conforme' y puede usarse como adjetivo invariable o seguido de 'con'.",
                    "ejemplo": "Una actuación acorde a las normas. Actuaron acorde con lo pactado.",
                    "ejercicio": "Corrige: 'Debe actuar acorde las reglas'.",
                    "suggestedAnswer": "Debe actuar acorde con las reglas (o 'acorde a las reglas')"
                }
            },
            {
                "id": 5084,
                "titulo": "Item 99",
                "categoria": "Gramatica",
                "tipo": "General",
                "nivel": 1,
                "puntos": 10,
                "contenido": {
                    "id": 99,
                    "name": "Uso de 'aplicar a' versus 'aplicar en'",
                    "category": "Preposiciones",
                    "teoria": "Se aplica una cosa 'a' alguien o algo, o se aplica 'en' un campo.",
                    "ejemplo": "Aplicaron la vacuna a los niños.",
                    "ejercicio": "Completa: 'Debemos aplicar la normativa ___ todos los trabajadores'.",
                    "suggestedAnswer": "a"
                }
            }
        ]
        
        self.archivo_json = 'ejercicios_ejemplo.json'
        with open(self.archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos_ejemplo, f, ensure_ascii=False, indent=2)
        print(f"{Color.VERDE}✅ Creado archivo: {self.archivo_json}{Color.FIN}")
    
    def leer_json(self):
        """Leer el archivo JSON"""
        try:
            with open(self.archivo_json, 'r', encoding='utf-8') as f:
                contenido = json.load(f)
            
            # Si es un objeto con key 'preguntas' o 'ejercicios'
            if isinstance(contenido, dict):
                if 'ejercicios' in contenido:
                    return contenido['ejercicios']
                elif 'preguntas' in contenido:
                    return contenido['preguntas']
                else:
                    return [contenido]
            elif isinstance(contenido, list):
                return contenido
            else:
                print(f"{Color.ROJO}❌ Formato JSON no reconocido{Color.FIN}")
                return []
        except Exception as e:
            print(f"{Color.ROJO}❌ Error leyendo JSON: {e}{Color.FIN}")
            return []
    
    @transaction.atomic
    def limpiar_ejercicios(self):
        """Eliminar todos los ejercicios actuales"""
        try:
            total = EjercicioLinguistico.objects.count()
            if total > 0:
                confirmar = input(f"{Color.AMARILLO}⚠️ Se eliminarán {total} ejercicios. ¿Continuar? (s/n): {Color.FIN}")
                if confirmar.lower() != 's':
                    print(f"{Color.AMARILLO}Operación cancelada{Color.FIN}")
                    return False
            
            EjercicioLinguistico.objects.all().delete()
            print(f"{Color.VERDE}✅ Eliminados {total} ejercicios{Color.FIN}")
            return True
        except Exception as e:
            print(f"{Color.ROJO}❌ Error eliminando: {e}{Color.FIN}")
            return False
    
    @transaction.atomic
    def cargar_ejercicios(self, datos):
        """Cargar ejercicios desde los datos JSON"""
        self.ejercicios_cargados = 0
        self.ejercicios_con_error = 0
        
        for item in datos:
            try:
                # Verificar campos obligatorios
                if not isinstance(item, dict):
                    continue
                
                titulo = item.get('titulo', 'Sin título')
                contenido = item.get('contenido', {})
                
                # Si contenido es string, intentar parsear
                if isinstance(contenido, str):
                    try:
                        contenido = json.loads(contenido)
                    except:
                        contenido = {'teoria': contenido}
                
                # Crear ejercicio
                ejercicio = EjercicioLinguistico(
                    titulo=titulo,
                    categoria=item.get('categoria', 'General'),
                    tipo=item.get('tipo', 'General'),
                    nivel=item.get('nivel', 1),
                    puntos=item.get('puntos', 10),
                    contenido=contenido if isinstance(contenido, dict) else {'teoria': str(contenido)}
                )
                ejercicio.save()
                self.ejercicios_cargados += 1
                
                if self.ejercicios_cargados % 100 == 0:
                    print(f"   Cargados {self.ejercicios_cargados} ejercicios...")
                    
            except Exception as e:
                self.ejercicios_con_error += 1
                print(f"{Color.ROJO}❌ Error en item {item.get('id', '?')}: {str(e)[:50]}{Color.FIN}")
        
        return self.ejercicios_cargados > 0
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas después de la carga"""
        total = EjercicioLinguistico.objects.count()
        categorias = EjercicioLinguistico.objects.values_list('categoria', flat=True).distinct()
        
        print(f"\n{Color.CYAN}{'='*60}{Color.FIN}")
        print(f"{Color.NEGRITA}📊 ESTADÍSTICAS FINALES{Color.FIN}")
        print(f"{Color.CYAN}{'='*60}{Color.FIN}")
        print(f"{Color.VERDE}✅ Total ejercicios: {total}{Color.FIN}")
        print(f"{Color.VERDE}✅ Categorías: {len(categorias)}{Color.FIN}")
        
        if total > 0:
            print(f"\n{Color.AZUL}📂 Categorías:{Color.FIN}")
            for cat in categorias[:10]:
                count = EjercicioLinguistico.objects.filter(categoria=cat).count()
                print(f"  - {cat}: {count} ejercicios")
            if len(categorias) > 10:
                print(f"  ... y {len(categorias) - 10} más")
    
    def ejecutar(self):
        """Ejecutar el proceso completo"""
        print(f"\n{Color.CYAN}{'='*60}{Color.FIN}")
        print(f"{Color.NEGRITA}🔄 RECARGADOR DE EJERCICIOS{Color.FIN}")
        print(f"{Color.CYAN}{'='*60}{Color.FIN}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 1. Buscar archivo JSON
        if not self.buscar_archivo_json():
            return
        
        # 2. Leer datos
        print(f"\n{Color.AZUL}📖 Leyendo archivo: {self.archivo_json}{Color.FIN}")
        datos = self.leer_json()
        if not datos:
            print(f"{Color.ROJO}❌ No se encontraron datos en el archivo{Color.FIN}")
            return
        
        print(f"{Color.VERDE}✅ Encontrados {len(datos)} ejercicios en el archivo{Color.FIN}")
        
        # 3. Mostrar ejemplo
        print(f"\n{Color.AZUL}📝 Ejemplo del archivo:{Color.FIN}")
        if datos:
            ejemplo = datos[0]
            print(f"  ID: {ejemplo.get('id', '?')}")
            print(f"  Título: {ejemplo.get('titulo', 'Sin título')}")
            print(f"  Categoría: {ejemplo.get('categoria', 'General')}")
            contenido = ejemplo.get('contenido', {})
            if isinstance(contenido, dict):
                print(f"  Teoría: {contenido.get('teoria', '')[:50]}...")
                print(f"  Ejercicio: {contenido.get('ejercicio', '')[:50]}...")
        
        # 4. Limpiar ejercicios actuales
        print(f"\n{Color.AMARILLO}🗑️ Limpiando ejercicios existentes...{Color.FIN}")
        if not self.limpiar_ejercicios():
            return
        
        # 5. Cargar nuevos ejercicios
        print(f"\n{Color.AZUL}📥 Cargando nuevos ejercicios...{Color.FIN}")
        if self.cargar_ejercicios(datos):
            print(f"\n{Color.VERDE}✅ Cargados {self.ejercicios_cargados} ejercicios{Color.FIN}")
            if self.ejercicios_con_error > 0:
                print(f"{Color.AMARILLO}⚠️ {self.ejercicios_con_error} errores encontrados{Color.FIN}")
        else:
            print(f"{Color.ROJO}❌ Error al cargar ejercicios{Color.FIN}")
        
        # 6. Mostrar estadísticas
        self.mostrar_estadisticas()
        
        print(f"\n{Color.VERDE}{'='*60}{Color.FIN}")
        print(f"{Color.NEGRITA}✅ PROCESO COMPLETADO{Color.FIN}")
        print(f"{Color.VERDE}{'='*60}{Color.FIN}")

if __name__ == "__main__":
    recargador = RecargadorEjercicios()
    recargador.ejecutar()

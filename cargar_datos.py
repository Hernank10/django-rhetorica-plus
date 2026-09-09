import os
import json
import sys
import django

sys.path.append('/workspaces/django-rhetorica-plus')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
django.setup()

from core.models import EjercicioLinguistico, TecnicaLinguistica, ContenidoJSON

def cargar_ejercicios():
    """Carga todos los JSON como ejercicios"""
    carpeta = 'data'
    contador = 0
    
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.json'):
            ruta = os.path.join(carpeta, archivo)
            print(f"📄 Procesando: {archivo}")
            
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                
                # Determinar categoría del nombre del archivo
                categoria = archivo.replace('.json', '').replace('_', ' ').title()
                
                if isinstance(datos, list):
                    for i, item in enumerate(datos):
                        titulo = item.get('titulo', item.get('nombre', f'Item {i+1}'))
                        tipo = item.get('tipo', item.get('categoria', 'General'))
                        
                        EjercicioLinguistico.objects.create(
                            titulo=titulo[:400],
                            contenido=item,
                            categoria=categoria,
                            tipo=tipo,
                            archivo_origen=archivo
                        )
                        contador += 1
                elif isinstance(datos, dict):
                    # Si es un diccionario, guardar como un solo ejercicio
                    EjercicioLinguistico.objects.create(
                        titulo=categoria,
                        contenido=datos,
                        categoria=categoria,
                        archivo_origen=archivo
                    )
                    contador += 1
                    
            except Exception as e:
                print(f"  ❌ Error en {archivo}: {e}")
    
    print(f"\n✅ Cargados {contador} ejercicios")

def cargar_contenidos_json():
    """Guarda los JSON completos como ContenidoJSON"""
    carpeta = 'data'
    contador = 0
    
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.json'):
            ruta = os.path.join(carpeta, archivo)
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                
                ContenidoJSON.objects.create(
                    nombre=archivo.replace('.json', ''),
                    archivo=archivo,
                    datos=datos,
                    categoria=archivo.replace('.json', '').split('_')[0] if '_' in archivo else 'General'
                )
                contador += 1
                print(f"📦 Guardado: {archivo}")
            except Exception as e:
                print(f"  ❌ Error en {archivo}: {e}")
    
    print(f"\n✅ Cargados {contador} contenidos JSON")

if __name__ == '__main__':
    print("🚀 INICIANDO CARGA DE DATOS\n")
    
    # Vaciar datos existentes (opcional)
    # EjercicioLinguistico.objects.all().delete()
    # ContenidoJSON.objects.all().delete()
    
    print("📚 Cargando ejercicios...")
    cargar_ejercicios()
    
    print("\n📦 Cargando contenidos JSON...")
    cargar_contenidos_json()
    
    print(f"\n📊 RESUMEN:")
    print(f"  Ejercicios: {EjercicioLinguistico.objects.count()}")
    print(f"  Técnicas: {TecnicaLinguistica.objects.count()}")
    print(f"  Contenidos JSON: {ContenidoJSON.objects.count()}")
    print("\n✅ CARGA COMPLETADA!")

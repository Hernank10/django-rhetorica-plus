import os
import json
import sys
import django

sys.path.append('/workspaces/django-rhetorica-plus')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
django.setup()

from core.models import EjercicioLinguistico, TecnicaLinguistica, ContenidoJSON

def cargar_ejercicios():
    carpeta = 'data'
    contador = 0
    errores = []
    
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.json'):
            ruta = os.path.join(carpeta, archivo)
            print(f"📄 Procesando: {archivo}")
            
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    
                # Intentar reparar JSON si es necesario
                try:
                    datos = json.loads(contenido)
                except json.JSONDecodeError as e:
                    print(f"  ⚠️ Error JSON en {archivo}: {e}")
                    errores.append(f"{archivo}: {e}")
                    continue
                
                categoria = archivo.replace('.json', '').replace('_', ' ').title()
                
                if isinstance(datos, list):
                    for i, item in enumerate(datos):
                        titulo = item.get('titulo', item.get('nombre', f'Item {i+1}'))
                        tipo = item.get('tipo', item.get('categoria', 'General'))
                        
                        EjercicioLinguistico.objects.create(
                            titulo=str(titulo)[:400],
                            contenido=item,
                            categoria=categoria,
                            tipo=str(tipo),
                            archivo_origen=archivo
                        )
                        contador += 1
                elif isinstance(datos, dict):
                    EjercicioLinguistico.objects.create(
                        titulo=categoria[:400],
                        contenido=datos,
                        categoria=categoria,
                        archivo_origen=archivo
                    )
                    contador += 1
                    
            except Exception as e:
                print(f"  ❌ Error en {archivo}: {e}")
                errores.append(f"{archivo}: {e}")
    
    print(f"\n✅ Cargados {contador} ejercicios")
    if errores:
        print(f"⚠️ Errores en {len(errores)} archivos")
        for error in errores[:5]:
            print(f"  - {error}")
    return contador

def cargar_contenidos_json():
    carpeta = 'data'
    contador = 0
    errores = []
    
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.json'):
            ruta = os.path.join(carpeta, archivo)
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    
                try:
                    datos = json.loads(contenido)
                except json.JSONDecodeError as e:
                    print(f"  ⚠️ Error JSON en {archivo}: {e}")
                    errores.append(f"{archivo}: {e}")
                    continue
                
                ContenidoJSON.objects.create(
                    nombre=archivo.replace('.json', ''),
                    archivo=archivo,
                    datos=datos,
                    categoria=archivo.replace('.json', '').split('_')[0] if '_' in archivo else 'General'
                )
                contador += 1
                print(f"  ✅ Guardado: {archivo}")
            except Exception as e:
                print(f"  ❌ Error en {archivo}: {e}")
                errores.append(f"{archivo}: {e}")
    
    print(f"\n✅ Cargados {contador} contenidos JSON")
    return contador

if __name__ == '__main__':
    print("🚀 INICIANDO CARGA DE DATOS\n")
    
    # Vaciar datos existentes
    EjercicioLinguistico.objects.all().delete()
    ContenidoJSON.objects.all().delete()
    
    print("📚 Cargando ejercicios...")
    ejercicios_cargados = cargar_ejercicios()
    
    print("\n📦 Cargando contenidos JSON...")
    contenidos_cargados = cargar_contenidos_json()
    
    print(f"\n📊 RESUMEN:")
    print(f"  Ejercicios: {EjercicioLinguistico.objects.count()}")
    print(f"  Técnicas: {TecnicaLinguistica.objects.count()}")
    print(f"  Contenidos JSON: {ContenidoJSON.objects.count()}")
    print("\n✅ CARGA COMPLETADA!")

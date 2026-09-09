import os
import sys
import django
import json
from bs4 import BeautifulSoup

sys.path.append('/workspaces/django-rhetorica-plus')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_retorica.settings')
django.setup()

from core.models import EjercicioLinguistico

def extraer_contenido_html(html_content):
    """Extrae el contenido relevante de un archivo HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    title = soup.find('title')
    titulo = title.text.strip() if title else 'Sin título'
    
    contenido = {}
    
    headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
    if headers:
        contenido['encabezados'] = [h.text.strip() for h in headers[:5]]
    
    paragraphs = soup.find_all('p')
    if paragraphs:
        contenido['parrafos'] = [p.text.strip() for p in paragraphs[:10]]
    
    # Buscar elementos interactivos
    ejercicios_html = soup.find_all(class_=lambda c: c and ('ejercicio' in c.lower() or 'flashcard' in c.lower() or 'pregunta' in c.lower()))
    if ejercicios_html:
        contenido['elementos_interactivos'] = len(ejercicios_html)
    
    texto_completo = soup.get_text(separator=' ', strip=True)
    contenido['texto_completo'] = texto_completo[:1000]
    
    return titulo, contenido

def extraer_contenido_json(json_content):
    """Extrae contenido de archivos JSON"""
    try:
        datos = json.loads(json_content)
        titulo = datos.get('titulo', datos.get('nombre', 'Sin título'))
        return titulo, datos
    except:
        return None, None

def cargar_todos_archivos():
    """Carga todos los archivos de la carpeta ejercicios_completos-lengua-castellana"""
    carpeta = 'data/ejercicios_completos-lengua-castellana'
    
    if not os.path.exists(carpeta):
        print(f"❌ La carpeta {carpeta} no existe")
        return
    
    archivos = os.listdir(carpeta)
    print(f"📂 Encontrados {len(archivos)} archivos en total")
    
    # Clasificar archivos por extensión
    html_files = [f for f in archivos if f.endswith('.html')]
    json_files = [f for f in archivos if f.endswith('.json')]
    docx_files = [f for f in archivos if f.endswith('.docx')]
    md_files = [f for f in archivos if f.endswith('.md')]
    sql_files = [f for f in archivos if f.endswith('.sql')]
    js_files = [f for f in archivos if f.endswith('.js')]
    otros = [f for f in archivos if not f.endswith(('.html', '.json', '.docx', '.md', '.sql', '.js'))]
    
    print(f"  - HTML: {len(html_files)} archivos")
    print(f"  - JSON: {len(json_files)} archivos")
    print(f"  - DOCX: {len(docx_files)} archivos")
    print(f"  - MD: {len(md_files)} archivos")
    print(f"  - SQL: {len(sql_files)} archivos")
    print(f"  - JS: {len(js_files)} archivos")
    print(f"  - Otros: {len(otros)} archivos")
    
    contador = 0
    errores = []
    
    # Procesar archivos HTML
    print(f"\n📄 Procesando {len(html_files)} archivos HTML...")
    for archivo in html_files:
        ruta = os.path.join(carpeta, archivo)
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            titulo, contenido = extraer_contenido_html(html_content)
            
            # Determinar categoría
            categoria = 'Lengua Castellana'
            if 'retórica' in archivo.lower() or 'retorica' in archivo.lower():
                categoria = 'Retórica'
            elif 'gramática' in archivo.lower() or 'gramatica' in archivo.lower():
                categoria = 'Gramática'
            elif 'sintaxis' in archivo.lower():
                categoria = 'Sintaxis'
            elif 'semántica' in archivo.lower() or 'semantica' in archivo.lower():
                categoria = 'Semántica'
            elif 'fonética' in archivo.lower() or 'fonetica' in archivo.lower():
                categoria = 'Fonética'
            elif 'literatura' in archivo.lower():
                categoria = 'Literatura'
            elif 'ortografía' in archivo.lower() or 'ortografia' in archivo.lower():
                categoria = 'Ortografía'
            elif 'etimología' in archivo.lower() or 'etimologia' in archivo.lower():
                categoria = 'Etimología'
            
            EjercicioLinguistico.objects.create(
                titulo=titulo[:400],
                contenido=contenido,
                categoria=categoria,
                tipo='HTML Interactivo',
                nivel=1,
                puntos=10,
                archivo_origen=archivo
            )
            contador += 1
            
            if contador % 100 == 0:
                print(f"  Procesados {contador} archivos...")
                
        except Exception as e:
            errores.append(f"{archivo}: {str(e)}")
    
    # Procesar archivos JSON
    print(f"\n📄 Procesando {len(json_files)} archivos JSON...")
    for archivo in json_files:
        ruta = os.path.join(carpeta, archivo)
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                json_content = f.read()
            
            titulo, datos = extraer_contenido_json(json_content)
            if titulo:
                categoria = archivo.split('.')[0].replace('_', ' ').title()
                EjercicioLinguistico.objects.create(
                    titulo=titulo[:400],
                    contenido=datos,
                    categoria=categoria[:100],
                    tipo='JSON',
                    nivel=1,
                    puntos=10,
                    archivo_origen=archivo
                )
                contador += 1
        except Exception as e:
            errores.append(f"{archivo}: {str(e)}")
    
    # Procesar archivos DOCX
    print(f"\n📄 Procesando {len(docx_files)} archivos DOCX...")
    for archivo in docx_files:
        ruta = os.path.join(carpeta, archivo)
        try:
            with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()[:2000]
            
            EjercicioLinguistico.objects.create(
                titulo=archivo.replace('.docx', '')[:400],
                contenido={'texto': content},
                categoria='Documento',
                tipo='DOCX',
                nivel=1,
                puntos=10,
                archivo_origen=archivo
            )
            contador += 1
        except:
            EjercicioLinguistico.objects.create(
                titulo=archivo.replace('.docx', '')[:400],
                contenido={'nota': 'Archivo DOCX no procesable directamente'},
                categoria='Documento',
                tipo='DOCX',
                nivel=1,
                puntos=10,
                archivo_origen=archivo
            )
            contador += 1
    
    print(f"\n✅ Cargados {contador} archivos en total")
    if errores:
        print(f"⚠️ Errores en {len(errores)} archivos")
        for error in errores[:5]:
            print(f"  - {error}")

if __name__ == '__main__':
    print("🚀 INICIANDO CARGA DE TODOS LOS ARCHIVOS")
    cargar_todos_archivos()
    print(f"📊 Total ejercicios: {EjercicioLinguistico.objects.count()}")

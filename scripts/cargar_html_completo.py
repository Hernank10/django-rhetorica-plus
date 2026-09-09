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
    
    # Extraer título
    title = soup.find('title')
    titulo = title.text.strip() if title else 'Sin título'
    
    # Extraer texto principal
    # Buscar en diferentes elementos comunes
    contenido = {}
    
    # Buscar encabezados
    headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
    if headers:
        contenido['encabezados'] = [h.text.strip() for h in headers[:5]]
    
    # Buscar párrafos
    paragraphs = soup.find_all('p')
    if paragraphs:
        contenido['parrafos'] = [p.text.strip() for p in paragraphs[:10]]
    
    # Buscar listas
    lists = soup.find_all(['ul', 'ol'])
    if lists:
        items = []
        for lst in lists[:3]:
            items.extend([li.text.strip() for li in lst.find_all('li')])
        contenido['lista'] = items[:10]
    
    # Buscar tablas
    tables = soup.find_all('table')
    if tables:
        table_data = []
        for table in tables[:2]:
            rows = table.find_all('tr')
            for row in rows[:5]:
                cells = row.find_all(['td', 'th'])
                table_data.append([cell.text.strip() for cell in cells])
        contenido['tabla'] = table_data
    
    # Texto completo (sin etiquetas)
    texto_completo = soup.get_text(separator=' ', strip=True)
    contenido['texto_completo'] = texto_completo[:1000]  # Limitamos a 1000 caracteres
    
    return titulo, contenido

def cargar_archivos_html():
    """Carga todos los archivos HTML de la carpeta ejercicios_completos-lengua-castellana"""
    carpeta = 'data/ejercicios_completos-lengua-castellana'
    
    if not os.path.exists(carpeta):
        print(f"❌ La carpeta {carpeta} no existe")
        return
    
    archivos = [f for f in os.listdir(carpeta) if f.endswith('.html')]
    print(f"📂 Encontrados {len(archivos)} archivos HTML")
    
    contador = 0
    errores = []
    
    for archivo in archivos:
        ruta = os.path.join(carpeta, archivo)
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            titulo, contenido = extraer_contenido_html(html_content)
            
            # Determinar categoría del nombre del archivo
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
            
            # Crear el ejercicio
            EjercicioLinguistico.objects.create(
                titulo=titulo[:400],
                contenido=contenido,
                categoria=categoria,
                tipo='HTML Completo',
                nivel=1,
                puntos=10,
                archivo_origen=archivo
            )
            contador += 1
            
            if contador % 50 == 0:
                print(f"📄 Procesados {contador} archivos...")
                
        except Exception as e:
            errores.append(f"{archivo}: {str(e)}")
    
    print(f"\n✅ Cargados {contador} ejercicios desde archivos HTML")
    if errores:
        print(f"⚠️ Errores en {len(errores)} archivos")
        for error in errores[:5]:
            print(f"  - {error}")

if __name__ == '__main__':
    print("🚀 INICIANDO CARGA DE ARCHIVOS HTML COMPLETOS")
    cargar_archivos_html()
    print(f"📊 Total ejercicios: {EjercicioLinguistico.objects.count()}")

#!/bin/bash
# Script de inicio completo con configuraciones

echo "🚀 INICIANDO RHETORICA+ CON CONFIGURACIONES"
echo "============================================"
echo ""

# 1. Verificar/crear directorios
echo "📁 Creando directorios necesarios..."
mkdir -p static static/css static/js static/images media

# 2. Generar datos de prueba
echo "📊 Generando datos de prueba..."
python scripts/generar_datos_prueba.py

# 3. Generar cursos
echo "📚 Generando cursos..."
python scripts/generar_cursos.py

# 4. Crear superusuario si no existe
echo "👤 Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    print('Creando superusuario...')
    User.objects.create_superuser('admin', 'admin@rhetorica.com', 'admin123')
    print('✅ Superusuario creado: admin / admin123')
"

# 5. Recoger archivos estáticos
echo "📦 Recogiendo archivos estáticos..."
python manage.py collectstatic --noinput

# 6. Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py migrate

# 7. Iniciar servidor
echo ""
echo "✅ ¡Sistema listo!"
echo ""
echo "🌐 Accede a:"
echo "  - Admin: http://localhost:8000/admin/"
echo "  - Dashboard: http://localhost:8000/dashboard/"
echo "  - Cursos: http://localhost:8000/cursos/"
echo "  - Biblioteca: http://localhost:8000/biblioteca/"
echo ""
echo "👤 Credenciales:"
echo "  - Usuario: admin"
echo "  - Contraseña: admin123"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

python manage.py runserver

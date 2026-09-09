#!/bin/bash
# Script de inicio rápido para Rhetorica Plus

echo "🚀 INICIANDO RHETORICA PLUS"
echo "============================"
echo ""

# 1. Activar entorno virtual
echo "📦 Activando entorno virtual..."
source venv/bin/activate

# 2. Generar datos si es necesario
echo "📊 Generando datos de prueba..."
python scripts/generar_datos_prueba.py

# 3. Ejecutar migraciones si es necesario
echo "🔄 Verificando migraciones..."
python manage.py migrate

# 4. Iniciar servidor
echo "🌐 Iniciando servidor..."
echo ""
echo "✅ Servidor iniciado en: http://localhost:8000/"
echo "📊 Dashboard: http://localhost:8000/dashboard/"
echo "📚 Biblioteca: http://localhost:8000/biblioteca/"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

python manage.py runserver

# Rhetorica+ - Plataforma interactiva para aprender retórica y etimología

[![Django](https://img.shields.io/badge/Django-6.0-brightgreen)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**Rhetorica+** es una aplicación web educativa de código abierto que ofrece **100 técnicas retóricas** y **100 raíces grecolatinas** mediante flashcards interactivas, ejercicios prácticos, exámenes aleatorios, dashboard de progreso y lector de voz integrado. Ideal para estudiantes de secundaria, bachillerato y primeros cursos universitarios.

![Vista previa](https://via.placeholder.com/800x400?text=Rhetorica+Preview) <!-- Puedes añadir una captura real más adelante -->

## 🚀 Características principales

- **100 figuras retóricas** con teoría, ejemplo, ejercicio de redacción y sugerencia de respuesta.
- **100 raíces etimológicas** con escritura original (griego y latín), ejemplos y autoevaluación.
- **Autenticación completa** (registro, login, logout, roles de usuario y administrador).
- **Dashboard personalizado** con puntos acumulados, nivel (Aprendiz → Maestro Retórico), progreso por categorías, recomendaciones y historial de actividades.
- **Generador de exámenes aleatorios** (retórica, etimología o mixto) con opción múltiple y corrección automática.
- **Panel de administración** para gestionar usuarios (crear, cambiar rol, eliminar) y ver estadísticas globales.
- **Lector de voz integrado** (Web Speech API) con botón flotante, selector de voz y control de velocidad.
- **Diseño responsive** con Bootstrap 5, adaptable a móviles, tablets y ordenadores.

## 📦 Tecnologías utilizadas

| Capa | Tecnología |
|------|-------------|
| Backend | Django 6.0, SQLite (desarrollo), SQLAlchemy (ORM) |
| Frontend | Bootstrap 5, Font Awesome 6, JavaScript vanilla |
| Autenticación | Django Auth + modelo personalizado `User` |
| API de voz | Web Speech API (síntesis de voz) |
| Datos | JSON estático con 100 entidades cada módulo |

## 🛠️ Instalación local

### Requisitos previos

- Python 3.10 o superior
- pip
- Entorno virtual (recomendado)

### Pasos

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/django-rhetorica-plus.git
cd django-rhetorica-plus

# Crear entorno virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt

# Realizar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario (opcional, para acceder al admin de Django)
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver
## 📦 Tecnologías utilizadas

| Capa | Tecnología |
|------|-------------|
| Backend | Django 6.0, SQLite (desarrollo), SQLAlchemy (ORM) |
| Frontend | Bootstrap 5, Font Awesome 6, JavaScript vanilla |
| Autenticación | Django Auth + modelo personalizado `User` |
| API de voz | Web Speech API (síntesis de voz) |
| Datos | JSON estático con 100 entidades cada módulo |

## 🛠️ Instalación local

### Requisitos previos

- Python 3.10 o superior
- pip
- Entorno virtual (recomendado)

### Pasos

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/django-rhetorica-plus.git
cd django-rhetorica-plus

# Crear entorno virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt

# Realizar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario (opcional, para acceder al admin de Django)
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver
Abre http://127.0.0.1:8000 en tu navegador.

Nota: Los datos de retórica y etimología se cargan desde los archivos data/retorica.json y data/etimologia.json. Si deseas modificar o ampliar el contenido, edita esos archivos y reinicia el servidor.

📁 Estructura del proyecto
text
django-rhetorica-plus/
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
├── data/
│   ├── retorica.json          # 100 técnicas
│   └── etimologia.json        # 100 raíces
├── core/                      # Aplicación principal
│   ├── models.py              # User, Respuesta, ProgresoCategoria
│   ├── views.py               # Lógica de negocio
│   ├── urls.py                # Rutas
│   ├── forms.py               # Formularios (registro)
│   ├── decorators.py          # Decorador admin_required
│   ├── templatetags/          # Filtros personalizados
│   └── templates/core/        # Plantillas HTML
├── django_retorica/           # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── static/                    # Archivos estáticos (CSS/JS adicionales)
🧪 Cómo usar la aplicación
Registro y autenticación
Ve a /registro para crear una cuenta.

Inicia sesión en /login.

El rol administrador se asigna manualmente desde el panel de administración o mediante el comando createsuperuser.

Flashcards interactivas
Retórica: Explora las 100 figuras. Escribe tu propio ejemplo y haz clic en “Verificar y guardar”. Si tu respuesta tiene más de 10 caracteres, obtendrás 10 puntos.

Etimología: Aprende raíces con su escritura original. Realiza ejercicios de creación de palabras y autoevalúate.

Dashboard
Muestra puntos acumulados, porcentaje de aciertos, nivel y progreso por categorías.

Proporciona recomendaciones personalizadas basadas en tu rendimiento.

Exámenes
Elige temática (retórica o etimología) y número de preguntas (5-50).

Responde y comprueba tus respuestas. Cada acierto suma 10 puntos.

Panel de administrador
Accede en /admin-panel (solo usuarios con is_admin=True).

Gestiona usuarios: crea, cambia rol o elimina.

Visualiza estadísticas globales del sistema.

Lector de voz
Botón flotante en la esquina inferior derecha: permite leer la página actual.

Controles para seleccionar voz en español y ajustar la velocidad de lectura.

📚 Datos incluidos
Retórica (100 figuras)
Entre otras: Anáfora, Metáfora, Ironía, Hipérbole, Oxímoron, Asíndeton, Polisíndeton, Quiasmo, Aliteración, Metonimia, Sinécdoque, Antítesis, Paradoja, Gradación, Interrogación retórica, Exclamación, Apóstrofe, Prosopopeya, Símil, Hipérbaton, Elipsis, Anacoluto, Paralelismo, etc.

Etimología (100 raíces)
Incluye raíces griegas y latinas como: bio (vida), geo (tierra), aqua (agua), chron (tiempo), phone (sonido), graph (escribir), logos (estudio), anthrop (humano), path (sentimiento), theos (dios), demos (pueblo), cracy (gobierno), arch (jefe), gen (origen), dict (decir), scrib (escribir), spec (mirar), aud (oír), vid (ver), ped (pie), man (mano), cap (cabeza), corp (cuerpo), mort (muerte), viv (vivir), ann (año), cent (cien), mill (mil), magn (grande), parv (pequeño), prim (primero), post (después), pre (antes), sub (debajo), super (sobre), trans (a través), anti (contra), pro (a favor), syn (junto), dia (a través), meta (más allá), para (junto a), peri (alrededor), ana (de nuevo), cata (hacia abajo), hyper (exceso), hypo (debajo), eu (bien), dys (mal), mono (uno), bi (dos), tri (tres), quadr (cuatro), penta (cinco), hexa (seis), hept (siete), octo (ocho), deca (diez), poly (muchos), olig (pocos), pan (todo), omni (todo), homo (igual), hetero (diferente), auto (uno mismo), pseudo (falso), neo (nuevo), paleo (antiguo), proto (primero), hemi (medio), semi (medio), equi (igual), multi (muchos), uni (uno), ambi (ambos), circum (alrededor), contra (contra), inter (entre), intra (dentro), extra (fuera), intro (dentro), retro (atrás), se (apartar), bene (bien), male (mal), nov (nuevo), veter (viejo), ver (verdad), cresc (crecer), lum (luz), bell (guerra), civ (ciudadano), leg (leer), duc (conducir), fer (llevar), fic (hacer), flect (doblar), plic (plegar), port (llevar), sed (sentar).

🤝 Contribuciones
Las contribuciones son bienvenidas. Por favor:

Fork el proyecto.

Crea una rama (git checkout -b feature/nueva-funcionalidad).

Haz commit de tus cambios (git commit -m 'Añadir nueva funcionalidad').

Push a la rama (git push origin feature/nueva-funcionalidad).

Abre un Pull Request.
✨ Créditos
Desarrollado como herramienta educativa para la enseñanza de retórica y etimología.

Inspiración: Aristóteles, Cicerón, Quintiliano, Gracián, Góngora, Quevedo y Valle-Inclán.

Tecnologías: Django, Bootstrap, Web Speech API.

¡Empieza tu viaje retórico hoy mismo! 📚🎙️

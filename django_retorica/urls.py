"""
URL Configuration for django_retorica project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import (
    index, login_view, registro_view, logout_view,
    dashboard_estudiante, dashboard_gamificacion,
    perfil_usuario, editar_perfil, cambiar_contrasena,
    certificaciones_lista, ver_tecnicas, enviar_respuesta
)

# Importar vistas de ejercicios
from core.views_ejercicios import detalle_ejercicio, practicar_ejercicio
from core.views_biblioteca import ejercicios_biblioteca

# Importar vistas de cursos (UN SOLO MÓDULO)
from core.views_cursos_completo import (
    lista_cursos, 
    detalle_curso, 
    ver_leccion, 
    ver_evaluacion,
    enviar_evaluacion,
    resultado_evaluacion,
    api_evaluacion_preguntas
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Autenticación
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('logout/', logout_view, name='logout'),
    
    # Perfil
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),
    path('perfil/cambiar-contrasena/', cambiar_contrasena, name='cambiar_contrasena'),
    
    # Dashboards
    path('dashboard/', dashboard_estudiante, name='dashboard_estudiante'),
    path('dashboard/gamificacion/', dashboard_gamificacion, name='dashboard_gamificacion'),
    
    # Ejercicios
    path('biblioteca/', ejercicios_biblioteca, name='ejercicios_biblioteca'),
    path('ejercicio/<int:ejercicio_id>/', detalle_ejercicio, name='detalle_ejercicio'),
    path('practicar/<int:ejercicio_id>/', practicar_ejercicio, name='practicar_ejercicio'),
    path('enviar-respuesta/<int:ejercicio_id>/', enviar_respuesta, name='enviar_respuesta'),
    
    # ============================================================
    # SECCIÓN DE CURSOS (UNICA DEFINICIÓN)
    # ============================================================
    path('cursos/', lista_cursos, name='lista_cursos'),
    path('cursos/<slug:curso_slug>/', detalle_curso, name='detalle_curso'),
    path('cursos/<slug:curso_slug>/modulo/<int:modulo_id>/leccion/<int:leccion_id>/', 
         ver_leccion, name='ver_leccion'),
    
    # Evaluaciones
    path('evaluacion/<int:evaluacion_id>/', ver_evaluacion, name='ver_evaluacion'),
    path('evaluacion/<int:evaluacion_id>/enviar/', enviar_evaluacion, name='enviar_evaluacion'),
    path('evaluacion/<int:evaluacion_id>/resultados/', resultado_evaluacion, name='resultado_evaluacion'),
    path('api/evaluacion/<int:evaluacion_id>/preguntas/', api_evaluacion_preguntas, name='api_evaluacion_preguntas'),
    
    # Técnicas
    path('tecnicas/', ver_tecnicas, name='ver_tecnicas'),
    
    # Certificaciones
    path('certificaciones/', certificaciones_lista, name='certificaciones_lista'),
]

# Archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

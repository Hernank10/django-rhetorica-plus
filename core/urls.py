from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Página principal
    path('', views.index, name='index'),
    
    # APIs
    path('api/ejercicios/', views.ejercicios_json, name='ejercicios_json'),
    path('api/tecnicas/', views.tecnicas_json, name='tecnicas_json'),
    path('api/contenidos/', views.contenidos_json, name='contenidos_json'),
    path('api/evaluaciones/', views.evaluaciones_json, name='evaluaciones_json'),
    path('api/perfil/', views.api_perfil, name='api_perfil'),
    path('api/verificar-usuario/', views.verificar_usuario, name='verificar_usuario'),
    
    # Dashboards
    path('dashboard/', views.dashboard_estudiante, name='dashboard_estudiante'),
    path('dashboard/gamificacion/', views.dashboard_gamificacion, name='dashboard_gamificacion'),
    path('dashboard/profesor/', views.dashboard_profesor, name='dashboard_profesor'),
    
    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recuperar-contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),
    
    # Perfil
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    
    # Certificaciones
    path('certificaciones/', views.certificaciones_lista, name='certificaciones_lista'),
    path('certificaciones/obtener/<int:certificacion_id>/', views.obtener_certificacion, name='obtener_certificacion'),
    path('verificar-certificacion/<str:codigo>/', views.verificar_certificacion, name='verificar_certificacion'),
    
    # Gestión de Ejercicios (Profesor)
    path('profesor/ejercicios/', views.gestion_ejercicios, name='gestion_ejercicios'),
    path('profesor/ejercicios/crear/', views.crear_ejercicio, name='crear_ejercicio'),
    path('profesor/ejercicios/editar/<int:ejercicio_id>/', views.editar_ejercicio, name='editar_ejercicio'),
    path('profesor/ejercicios/eliminar/<int:ejercicio_id>/', views.eliminar_ejercicio, name='eliminar_ejercicio'),
    
    # Gestión de Técnicas (Profesor)
    path('profesor/tecnicas/', views.gestion_tecnicas, name='gestion_tecnicas'),
    path('profesor/tecnicas/crear/', views.crear_tecnica, name='crear_tecnica'),
    path('profesor/tecnicas/editar/<int:tecnica_id>/', views.editar_tecnica, name='editar_tecnica'),
    path('profesor/tecnicas/eliminar/<int:tecnica_id>/', views.eliminar_tecnica, name='eliminar_tecnica'),
    
    # Gestión de Contenidos (Profesor)
    path('profesor/contenidos/', views.gestion_contenidos, name='gestion_contenidos'),
    path('profesor/contenidos/crear/', views.crear_contenido, name='crear_contenido'),
    path('profesor/contenidos/editar/<int:contenido_id>/', views.editar_contenido, name='editar_contenido'),
    path('profesor/contenidos/eliminar/<int:contenido_id>/', views.eliminar_contenido, name='eliminar_contenido'),
    
    # Gestión de Evaluaciones (Profesor)
    path('profesor/evaluaciones/', views.gestion_evaluaciones, name='gestion_evaluaciones'),
    path('profesor/evaluaciones/crear/', views.crear_evaluacion, name='crear_evaluacion'),
    path('profesor/evaluaciones/editar/<int:evaluacion_id>/', views.editar_evaluacion, name='editar_evaluacion'),
    path('profesor/evaluaciones/eliminar/<int:evaluacion_id>/', views.eliminar_evaluacion, name='eliminar_evaluacion'),
    
    # Gestión de Estudiantes (Profesor)
    path('profesor/estudiantes/', views.gestion_estudiantes, name='gestion_estudiantes'),
    path('profesor/estudiantes/<int:estudiante_id>/', views.detalle_estudiante, name='detalle_estudiante'),
    
    # Gestión de Logros (Profesor)
    path('profesor/logros/', views.gestion_logros, name='gestion_logros'),
    path('profesor/logros/crear/', views.crear_logro, name='crear_logro'),
    path('profesor/logros/editar/<int:logro_id>/', views.editar_logro, name='editar_logro'),
    path('profesor/logros/eliminar/<int:logro_id>/', views.eliminar_logro, name='eliminar_logro'),
    
    # Gestión de Usuarios (Admin)
    path('admin/usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('admin/usuarios/<int:usuario_id>/toggle/', views.toggle_usuario_activo, name='toggle_usuario_activo'),
    
    # Carga Masiva y Exportación
    path('profesor/carga-masiva/', views.carga_masiva, name='carga_masiva'),
    path('profesor/exportar/ejercicios/', views.exportar_ejercicios, name='exportar_ejercicios'),
    path('profesor/exportar/tecnicas/', views.exportar_tecnicas, name='exportar_tecnicas'),
    path('profesor/exportar/contenidos/', views.exportar_contenidos, name='exportar_contenidos'),
    path('profesor/estadisticas/', views.estadisticas_contenido, name='estadisticas_contenido'),
    
    # Visualización Pública
    path('ejercicio/<int:ejercicio_id>/', views.detalle_ejercicio, name='detalle_ejercicio'),
    path('tecnica/<int:tecnica_id>/', views.ver_tecnica, name='ver_tecnica'),
    path('contenido/<int:contenido_id>/', views.ver_contenido, name='ver_contenido'),
    
    # Búsqueda
    path('buscar/ejercicios/', views.buscar_ejercicios, name='buscar_ejercicios'),
    path('buscar/tecnicas/', views.buscar_tecnicas, name='buscar_tecnicas'),
    
    # Práctica y Evaluaciones
    path('practicar/<int:ejercicio_id>/', views.practicar_ejercicio, name='practicar_ejercicio'),
    path('evaluacion/<int:evaluacion_id>/', views.evaluacion_detalle, name='evaluacion_detalle'),
    path('evaluacion/<int:evaluacion_id>/enviar/', views.enviar_evaluacion, name='enviar_evaluacion'),
]

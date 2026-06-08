from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('retorica/', views.retorica, name='retorica'),
    path('etimologia/', views.etimologia, name='etimologia'),
    path('examen/', views.examen_form, name='examen_form'),
    path('api/generar_preguntas/', views.api_generar_preguntas, name='api_generar'),
    path('api/guardar_respuesta/', views.api_guardar_respuesta, name='api_guardar'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/nuevo/', views.admin_nuevo_usuario, name='admin_nuevo_usuario'),
    path('admin-panel/toggle/<int:user_id>/', views.toggle_admin, name='toggle_admin'),
    path('admin-panel/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('proyecto/', views.proyecto, name='proyecto'),
]

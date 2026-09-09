from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Respuesta, ProgresoCategoria, EjercicioLinguistico, TecnicaLinguistica, ContenidoJSON

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'points', 'nivel', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Progreso', {'fields': ('points', 'nivel', 'is_admin')}),
    )

@admin.register(Respuesta)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_ejercicio', 'item_id', 'es_correcta', 'puntuacion', 'fecha')
    list_filter = ('es_correcta', 'tipo_ejercicio', 'fecha')
    search_fields = ('user__username', 'respuesta_usuario')

@admin.register(ProgresoCategoria)
class ProgresoCategoriaAdmin(admin.ModelAdmin):
    list_display = ('user', 'categoria', 'aciertos', 'intentos', 'porcentaje')
    list_filter = ('categoria',)

@admin.register(EjercicioLinguistico)
class EjercicioLinguisticoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'tipo', 'creado_en')
    search_fields = ('titulo', 'categoria', 'tipo')
    list_filter = ('categoria', 'tipo', 'creado_en')

@admin.register(TecnicaLinguistica)
class TecnicaLinguisticaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'creado_en')
    search_fields = ('nombre', 'descripcion', 'categoria')
    list_filter = ('categoria', 'creado_en')

@admin.register(ContenidoJSON)
class ContenidoJSONAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'creado_en')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria', 'creado_en')

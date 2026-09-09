"""
Modelos para preguntas generadas automáticamente
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PreguntaGenerada(models.Model):
    """Modelo para almacenar preguntas generadas"""
    
    TIPOS_PREGUNTA = [
        ('correccion', 'Corrección'),
        ('completar', 'Completar'),
        ('reescribir', 'Reescribir'),
        ('elegir', 'Elegir'),
        ('explicar', 'Explicar'),
        ('verdadero_falso', 'Verdadero/Falso'),
        ('relacionar', 'Relacionar'),
        ('ordenar', 'Ordenar'),
        ('multiple_choice', 'Opción Múltiple'),
        ('desarrollo', 'Desarrollo'),
    ]
    
    NIVELES_DIFICULTAD = [
        (1, 'Principiante'),
        (2, 'Intermedio'),
        (3, 'Avanzado'),
        (4, 'Experto'),
    ]
    
    # Datos principales
    tipo = models.CharField(max_length=20, choices=TIPOS_PREGUNTA)
    titulo = models.CharField(max_length=200)
    enunciado = models.TextField()
    respuesta_correcta = models.TextField()
    
    # Campos específicos según tipo
    opciones = models.JSONField(null=True, blank=True)  # Para multiple_choice y elegir
    pista = models.TextField(blank=True)
    
    # Metadatos
    dificultad = models.IntegerField(choices=NIVELES_DIFICULTAD, default=1)
    puntos = models.IntegerField(default=10)
    categoria = models.CharField(max_length=100, blank=True)
    ejercicio_base_id = models.IntegerField(null=True, blank=True)
    
    # Auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(default=timezone.now)
    usado_en = models.IntegerField(default=0)  # Veces que se ha usado
    activa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['tipo', 'dificultad']),
            models.Index(fields=['activa']),
        ]
    
    def __str__(self):
        return f"{self.titulo} ({self.tipo})"
    
    def get_tipo_emoji(self):
        """Obtener emoji según tipo de pregunta"""
        emojis = {
            'correccion': '✏️',
            'completar': '📝',
            'reescribir': '🔄',
            'elegir': '✅',
            'explicar': '💡',
            'verdadero_falso': '⚖️',
            'relacionar': '🔗',
            'ordenar': '📋',
            'multiple_choice': '🔘',
            'desarrollo': '📖',
        }
        return emojis.get(self.tipo, '📌')
    
    def get_color_tipo(self):
        """Obtener color según tipo de pregunta"""
        colores = {
            'correccion': 'danger',
            'completar': 'primary',
            'reescribir': 'success',
            'elegir': 'warning',
            'explicar': 'purple',
            'verdadero_falso': 'info',
            'relacionar': 'orange',
            'ordenar': 'dark',
            'multiple_choice': 'teal',
            'desarrollo': 'red',
        }
        return colores.get(self.tipo, 'secondary')


class RespuestaPregunta(models.Model):
    """Modelo para almacenar respuestas de estudiantes"""
    
    pregunta = models.ForeignKey(PreguntaGenerada, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    respuesta = models.TextField()
    es_correcta = models.BooleanField(default=False)
    puntos_obtenidos = models.IntegerField(default=0)
    
    fecha = models.DateTimeField(default=timezone.now)
    tiempo_respuesta = models.IntegerField(null=True, blank=True)  # Segundos
    
    class Meta:
        ordering = ['-fecha']
        unique_together = ['pregunta', 'usuario']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.pregunta.titulo[:30]}"

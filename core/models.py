from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    points = models.IntegerField(default=0)
    nivel = models.CharField(max_length=20, default='Aprendiz')
    is_admin = models.BooleanField(default=False)
    estrellas = models.IntegerField(default=0, help_text="Estrellas de oro acumuladas")
    medallas = models.JSONField(default=list, blank=True, help_text="Lista de medallas obtenidas")
    insignias = models.JSONField(default=list, blank=True, help_text="Lista de insignias obtenidas")
    certificaciones = models.JSONField(default=list, blank=True, help_text="Lista de certificaciones obtenidas")
    racha = models.IntegerField(default=0, help_text="Días consecutivos practicando")
    ultima_actividad = models.DateTimeField(null=True, blank=True)
    total_ejercicios_completados = models.IntegerField(default=0)
    tasa_aciertos = models.FloatField(default=0.0)
    nivel_experiencia = models.IntegerField(default=1)
    
    # Agregar related_name para evitar conflictos con auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='core_user_set',
        related_query_name='core_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='core_user_set',
        related_query_name='core_user',
    )

    def save(self, *args, **kwargs):
        # Actualizar nivel basado en puntos
        if self.points < 100:
            self.nivel = 'Aprendiz'
            self.nivel_experiencia = 1
        elif self.points < 300:
            self.nivel = 'Conocedor'
            self.nivel_experiencia = 2
        elif self.points < 600:
            self.nivel = 'Experto'
            self.nivel_experiencia = 3
        elif self.points < 1000:
            self.nivel = 'Maestro Retórico'
            self.nivel_experiencia = 4
        elif self.points < 2000:
            self.nivel = 'Sabio'
            self.nivel_experiencia = 5
        else:
            self.nivel = 'Gran Orador'
            self.nivel_experiencia = 6
        
        # Calcular tasa de aciertos
        total_respuestas = Respuesta.objects.filter(user=self).count()
        if total_respuestas > 0:
            correctas = Respuesta.objects.filter(user=self, es_correcta=True).count()
            self.tasa_aciertos = round((correctas / total_respuestas) * 100, 2)
        
        super().save(*args, **kwargs)

class Respuesta(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='respuestas')
    tipo_ejercicio = models.CharField(max_length=50)
    item_id = models.IntegerField()
    respuesta_usuario = models.TextField()
    es_correcta = models.BooleanField(default=False)
    puntuacion = models.IntegerField(default=0)
    tiempo_segundos = models.IntegerField(default=0, help_text="Tiempo en segundos")
    fecha = models.DateTimeField(default=timezone.now)
    intento_numero = models.IntegerField(default=1)
    feedback = models.TextField(blank=True, null=True)

class ProgresoCategoria(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progreso')
    categoria = models.CharField(max_length=100)
    aciertos = models.IntegerField(default=0)
    intentos = models.IntegerField(default=0)
    nivel_dominio = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    estrellas_obtenidas = models.IntegerField(default=0)

    @property
    def porcentaje(self):
        if self.intentos == 0:
            return 0
        return round((self.aciertos / self.intentos) * 100)

class Evaluacion(models.Model):
    TIPO_CHOICES = [
        ('diagnostico', 'Diagnóstico'),
        ('formativa', 'Formativa'),
        ('sumativa', 'Sumativa'),
        ('final', 'Final'),
    ]
    
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=100)
    nivel_requerido = models.IntegerField(default=1)
    puntos_base = models.IntegerField(default=10)
    duracion_minutos = models.IntegerField(default=30)
    preguntas = models.JSONField(default=list)
    creada_en = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} ({self.tipo})"

class ResultadoEvaluacion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluaciones')
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE)
    puntaje = models.IntegerField(default=0)
    respuestas = models.JSONField(default=list)
    tiempo_utilizado = models.IntegerField(default=0)
    completada = models.BooleanField(default=False)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    calificacion = models.CharField(max_length=20, blank=True, null=True)
    feedback_general = models.TextField(blank=True, null=True)

    def calcular_calificacion(self):
        if self.puntaje >= 90:
            return 'Excelente'
        elif self.puntaje >= 75:
            return 'Bueno'
        elif self.puntaje >= 60:
            return 'Regular'
        else:
            return 'Necesita Mejorar'

class Logro(models.Model):
    TIPO_CHOICES = [
        ('insignia', 'Insignia'),
        ('medalla', 'Medalla'),
        ('estrella', 'Estrella'),
        ('certificacion', 'Certificación'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    icono = models.CharField(max_length=100, help_text="Clase de Font Awesome o emoji")
    color = models.CharField(max_length=50, default='gold')
    puntos_requeridos = models.IntegerField(default=0)
    nivel_requerido = models.IntegerField(default=1)
    categoria_requerida = models.CharField(max_length=100, blank=True, null=True)
    ejercicios_completados_requeridos = models.IntegerField(default=0)
    tasa_aciertos_requerida = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

class LogroObtenido(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logros_obtenidos')
    logro = models.ForeignKey(Logro, on_delete=models.CASCADE)
    fecha_obtenida = models.DateTimeField(auto_now_add=True)
    notificado = models.BooleanField(default=False)

class Certificacion(models.Model):
    NIVEL_CHOICES = [
        ('bronce', 'Bronce'),
        ('plata', 'Plata'),
        ('oro', 'Oro'),
        ('platino', 'Platino'),
        ('diamante', 'Diamante'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    requisitos = models.JSONField(default=dict)
    imagen = models.CharField(max_length=200, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.nivel}"

class CertificacionObtenida(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificaciones_obtenidas')
    certificacion = models.ForeignKey(Certificacion, on_delete=models.CASCADE)
    fecha_obtenida = models.DateTimeField(auto_now_add=True)
    codigo_verificacion = models.CharField(max_length=100, unique=True)
    url_verificacion = models.URLField(blank=True, null=True)

class EjercicioLinguistico(models.Model):
    titulo = models.CharField(max_length=500, verbose_name="Título")
    contenido = models.JSONField(default=dict, verbose_name="Contenido completo")
    categoria = models.CharField(max_length=200, blank=True, null=True)
    tipo = models.CharField(max_length=100, blank=True, null=True)
    nivel = models.IntegerField(default=1, help_text="Nivel de dificultad")
    puntos = models.IntegerField(default=10)
    archivo_origen = models.CharField(max_length=300, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Ejercicio Lingüístico"
        verbose_name_plural = "Ejercicios Lingüísticos"
        ordering = ['-creado_en']
    
    def __str__(self):
        return self.titulo[:100]

class TecnicaLinguistica(models.Model):
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=200, blank=True, null=True)
    nivel = models.IntegerField(default=1)
    archivo_origen = models.CharField(max_length=300, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Técnica Lingüística"
        verbose_name_plural = "Técnicas Lingüísticas"
    
    def __str__(self):
        return self.nombre[:100]

class ContenidoJSON(models.Model):
    nombre = models.CharField(max_length=300)
    archivo = models.CharField(max_length=300)
    datos = models.JSONField(default=dict)
    categoria = models.CharField(max_length=200, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Contenido JSON"
        verbose_name_plural = "Contenidos JSON"
    
    def __str__(self):
        return self.nombre[:100]

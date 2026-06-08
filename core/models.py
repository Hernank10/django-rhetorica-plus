from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    points = models.IntegerField(default=0)
    nivel = models.CharField(max_length=20, default='Aprendiz')
    is_admin = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.points < 100:
            self.nivel = 'Aprendiz'
        elif self.points < 300:
            self.nivel = 'Conocedor'
        elif self.points < 600:
            self.nivel = 'Experto'
        else:
            self.nivel = 'Maestro Retórico'
        super().save(*args, **kwargs)

class Respuesta(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='respuestas')
    tipo_ejercicio = models.CharField(max_length=50)
    item_id = models.IntegerField()
    respuesta_usuario = models.TextField()
    es_correcta = models.BooleanField(default=False)
    puntuacion = models.IntegerField(default=0)
    fecha = models.DateTimeField(default=timezone.now)

class ProgresoCategoria(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progreso')
    categoria = models.CharField(max_length=100)
    aciertos = models.IntegerField(default=0)
    intentos = models.IntegerField(default=0)

    @property
    def porcentaje(self):
        if self.intentos == 0:
            return 0
        return round((self.aciertos / self.intentos) * 100)

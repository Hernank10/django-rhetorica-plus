"""
Modelos para el sistema de cursos
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .models import EjercicioLinguistico, TecnicaLinguistica

class Curso(models.Model):
    """Modelo principal de curso"""
    
    NIVELES = [
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
        ('experto', 'Experto'),
    ]
    
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('publicado', 'Publicado'),
        ('archivado', 'Archivado'),
    ]
    
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    descripcion = models.TextField()
    objetivo = models.TextField(blank=True)
    nivel = models.CharField(max_length=20, choices=NIVELES, default='principiante')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='borrador')
    duracion_estimada = models.IntegerField(help_text="Duración estimada en horas", default=10)
    puntos_totales = models.IntegerField(default=0)
    
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cursos_creados')
    tecnicas_relacionadas = models.ManyToManyField(TecnicaLinguistica, blank=True)
    
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(auto_now=True)
    publicado_en = models.DateTimeField(null=True, blank=True)
    
    estudiantes_inscritos = models.IntegerField(default=0)
    calificacion_promedio = models.FloatField(default=0.0)
    numero_revisiones = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-creado_en']
    
    def __str__(self):
        return self.titulo
    
    def get_duracion_texto(self):
        if self.duracion_estimada < 1:
            return f"{int(self.duracion_estimada * 60)} minutos"
        return f"{self.duracion_estimada} horas"
    
    def get_progreso_usuario(self, usuario):
        modulos = self.modulos.all()
        total_lecciones = sum(m.lecciones.count() for m in modulos)
        if total_lecciones == 0:
            return 0
        return 0  # Implementar después


class Modulo(models.Model):
    """Módulo dentro de un curso"""
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='modulos')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    orden = models.IntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['orden']
        unique_together = ['curso', 'orden']
    
    def __str__(self):
        return f"{self.curso.titulo} - {self.titulo}"


class Leccion(models.Model):
    """Lección dentro de un módulo"""
    
    TIPOS = [
        ('teoria', 'Teoría'),
        ('practica', 'Práctica'),
        ('evaluacion', 'Evaluación'),
        ('mixto', 'Mixto'),
    ]
    
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='lecciones')
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default='teoria')
    orden = models.IntegerField(default=0)
    
    ejercicios_relacionados = models.ManyToManyField(EjercicioLinguistico, blank=True)
    tecnicas_relacionadas = models.ManyToManyField(TecnicaLinguistica, blank=True)
    
    duracion_estimada = models.IntegerField(help_text="Duración en minutos", default=15)
    puntos = models.IntegerField(default=10)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['orden']
        unique_together = ['modulo', 'orden']
    
    def __str__(self):
        return f"{self.modulo.titulo} - {self.titulo}"


class ProgresoUsuario(models.Model):
    """Progreso del usuario en lecciones"""
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progreso_lecciones')
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE, related_name='progresos')
    completado = models.BooleanField(default=False)
    puntaje_obtenido = models.IntegerField(default=0)
    intentos = models.IntegerField(default=0)
    tiempo_dedicado = models.IntegerField(help_text="Tiempo en segundos", default=0)
    ultima_actividad = models.DateTimeField(default=timezone.now)
    completado_en = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['usuario', 'leccion']
    
    def __str__(self):
        estado = "✅" if self.completado else "⏳"
        return f"{estado} {self.usuario.username} - {self.leccion.titulo}"

class EvaluacionCurso(models.Model):
    """Modelo para evaluaciones de cursos"""
    
    TIPOS_EVALUACION = [
        ('diagnostica', 'Diagnóstica'),
        ('formativa', 'Formativa'),
        ('sumativa', 'Sumativa'),
        ('final', 'Final'),
    ]
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='evaluaciones')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_EVALUACION, default='formativa')
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, null=True, blank=True, related_name='evaluaciones')
    
    # Configuración
    preguntas_por_evaluacion = models.IntegerField(default=10)
    tiempo_limite = models.IntegerField(help_text="Tiempo en minutos", default=30)
    puntaje_maximo = models.IntegerField(default=100)
    intentos_permitidos = models.IntegerField(default=3)
    
    # Fechas
    creado_en = models.DateTimeField(auto_now_add=True)
    disponible_desde = models.DateTimeField(null=True, blank=True)
    disponible_hasta = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Evaluación: {self.titulo} - {self.curso.titulo}"


class PreguntaEvaluacion(models.Model):
    """Modelo para preguntas de evaluaciones"""
    
    TIPOS_PREGUNTA = [
        ('multiple', 'Opción Múltiple'),
        ('verdadero_falso', 'Verdadero/Falso'),
        ('completar', 'Completar'),
        ('desarrollo', 'Desarrollo'),
        ('correccion', 'Corrección'),
    ]
    
    evaluacion = models.ForeignKey(EvaluacionCurso, on_delete=models.CASCADE, related_name='preguntas')
    ejercicio = models.ForeignKey(EjercicioLinguistico, on_delete=models.SET_NULL, null=True, blank=True)
    
    enunciado = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS_PREGUNTA, default='multiple')
    opciones = models.JSONField(null=True, blank=True)
    respuesta_correcta = models.TextField()
    puntaje = models.IntegerField(default=10)
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
    
    def __str__(self):
        return f"{self.tipo}: {self.enunciado[:50]}..."


class ResultadoEvaluacionCurso(models.Model):
    """Modelo para resultados de evaluaciones"""
    
    evaluacion = models.ForeignKey(EvaluacionCurso, on_delete=models.CASCADE, related_name='resultados')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resultados_evaluaciones')
    
    puntaje_obtenido = models.IntegerField(default=0)
    puntaje_maximo = models.IntegerField(default=0)
    respuestas = models.JSONField(default=dict)
    intento = models.IntegerField(default=1)
    
    completado = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    tiempo_empleado = models.IntegerField(help_text="Tiempo en segundos", default=0)
    
    class Meta:
        unique_together = ['evaluacion', 'usuario', 'intento']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.evaluacion.titulo} - {self.puntaje_obtenido}/{self.puntaje_maximo}"

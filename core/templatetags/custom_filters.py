from django import template

register = template.Library()

@register.filter
def total_lecciones(curso):
    """Devuelve el total de lecciones de un curso"""
    total = 0
    for modulo in curso.modulos.all():
        total += modulo.lecciones.count()
    return total

@register.filter
def total_modulos(curso):
    """Devuelve el total de módulos de un curso"""
    return curso.modulos.count()

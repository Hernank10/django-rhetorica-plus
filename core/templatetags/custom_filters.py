from django import template

register = template.Library()

@register.filter(name='in_list')
def in_list(value, arg):
    """
    Verifica si un valor está en una lista.
    Uso: {% if value|in_list:lista %}
    """
    if not arg:
        return False
    return value in arg

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Obtiene un item de un diccionario.
    Uso: {{ diccionario|get_item:key }}
    """
    return dictionary.get(key, '')

@register.filter(name='dict_values')
def dict_values(dictionary):
    """
    Obtiene los valores de un diccionario.
    Uso: {{ diccionario|dict_values }}
    """
    if isinstance(dictionary, dict):
        return dictionary.values()
    return []

@register.filter(name='has_key')
def has_key(dictionary, key):
    """
    Verifica si un diccionario tiene una clave.
    Uso: {% if diccionario|has_key:key %}
    """
    if not dictionary:
        return False
    return key in dictionary

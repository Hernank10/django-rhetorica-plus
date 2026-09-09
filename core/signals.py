"""Señales para sincronizar usuarios entre modelos"""

from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import User as CoreUser
from django.contrib.auth.models import User as AuthUser

@receiver(post_save, sender=AuthUser)
def sync_user_to_core(sender, instance, created, **kwargs):
    """
    Cuando se crea un usuario en auth.User, se crea automáticamente en core.User
    """
    if created:
        # Verificar si ya existe en core.User
        if not CoreUser.objects.filter(username=instance.username).exists():
            CoreUser.objects.create_user(
                username=instance.username,
                email=instance.email,
                password=instance.password  # La contraseña se sincroniza
            )
            print(f"✅ Usuario {instance.username} sincronizado con core.User")

@receiver(post_save, sender=CoreUser)
def sync_user_to_auth(sender, instance, created, **kwargs):
    """
    Cuando se crea un usuario en core.User, se crea automáticamente en auth.User
    """
    if created:
        # Verificar si ya existe en auth.User
        AuthUser = get_user_model()
        if not AuthUser.objects.filter(username=instance.username).exists():
            AuthUser.objects.create_user(
                username=instance.username,
                email=instance.email,
                password=instance.password
            )
            print(f"✅ Usuario {instance.username} sincronizado con auth.User")

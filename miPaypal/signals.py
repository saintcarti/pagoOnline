from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser

# Ejemplo de señal (puedes personalizarlo)
@receiver(post_save, sender=CustomUser)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        print(f"Nuevo usuario creado: {instance.username}")
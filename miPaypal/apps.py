from django.apps import AppConfig

class MiPaypalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'miPaypal'
    
    def ready(self):
        pass  # Elimina la línea import miPaypal.signals
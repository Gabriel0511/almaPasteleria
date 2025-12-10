from django.apps import AppConfig


class RecetasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recetas'

    def ready(self):
        # Importar señales
        import recetas.models

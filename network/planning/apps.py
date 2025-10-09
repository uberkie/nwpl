from django.apps import AppConfig


class PlanningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'planning'

    def ready(self):
        # Import signal handlers to register them
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass

from django.apps import AppConfig


class TraymanagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'traymanagement'
    verbose_name = 'Tray Management'
    
    def ready(self):
        import traymanagement.signals
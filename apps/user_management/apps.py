from django.apps import AppConfig


class UserManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.user_management'
    verbose_name = 'User Management'

    def ready(self):
        """
        Import any signals here
        """
        try:
            import apps.user_management.signals
        except ImportError:
            pass

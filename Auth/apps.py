from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = 'Auth'


    def ready(self):
        from Auth import signals

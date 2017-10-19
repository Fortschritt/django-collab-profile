from django.apps import AppConfig


class CollabProfileConfig(AppConfig):
    name = 'collab_profile'

    def ready(self):
        # register our signals
        from . import signals

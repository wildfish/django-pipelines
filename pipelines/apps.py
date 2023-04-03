from django.apps import AppConfig


class PipelinesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pipelines"
    verbose_name = "Django Pipelines"

    def ready(self):
        from pipelines.registry import pipeline_registry
        from pipelines.tasks import task_registry

        pipeline_registry.autodiscover()
        task_registry.autodiscover()

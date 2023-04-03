from django.urls import include, path


urlpatterns = [
    path("", include("pipelines.urls")),
]

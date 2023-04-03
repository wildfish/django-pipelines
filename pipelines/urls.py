from django.contrib import admin
from django.urls import path

from pipelines import views


admin.autodiscover()

app_name = "pipelines"

urlpatterns = [
    path(
        "",
        views.PipelineListView.as_view(),
        name="list",
    ),
    path(
        "<str:slug>/runs/",
        views.PipelineExecutionListView.as_view(),
        name="pipeline-execution-list",
    ),
    path(
        "<str:slug>/start/",
        views.PipelineStartView.as_view(),
        name="start",
    ),
    path(
        "<str:run_id>/results/",
        views.PipelineResultView.as_view(),
        name="results",
    ),
    path(
        "<str:run_id>/results/list/",
        views.TaskResultListView.as_view(),
        name="results-list",
    ),
    path(
        "<str:run_id>/logs/",
        views.LogListView.as_view(),
        name="logs-list",
    ),
    path(
        "<str:run_id>/logs-filter/",
        views.LogFilterView.as_view(),
        name="logs-filter",
    ),
    path(
        "task-result/<str:pk>/rerun/",
        views.TaskResultReRunView.as_view(),
        name="rerun-task",
    ),
]

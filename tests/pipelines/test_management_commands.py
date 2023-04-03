from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.utils.timezone import now

import pytest
from model_bakery import baker

from pipelines.models import (
    OrmPipelineExecution,
    OrmPipelineResult,
    OrmTaskExecution,
    OrmTaskResult,
    PipelineLog,
)


pytest_plugins = [
    "tests.pipelines.fixtures",
]

pytestmark = pytest.mark.django_db


def test_clear_tasks_and_logs__all_deleted(freezer):
    today = now().today()

    pipeline_execution = baker.make_recipe(
        "pipelines.fake_pipeline_execution", run_id="123", started=today
    )
    pipeline_result = baker.make_recipe(
        "pipelines.fake_pipeline_result", execution=pipeline_execution
    )
    task_execution = baker.make_recipe(
        "pipelines.fake_task_execution", pipeline_result=pipeline_result
    )
    baker.make_recipe(
        "pipelines.fake_task_result", execution=task_execution, _quantity=3
    )
    baker.make_recipe("pipelines.fake_pipeline_log", run_id="123", _quantity=3)

    freezer.move_to(today + timedelta(days=11))

    out = StringIO()
    call_command("clear_tasks_and_logs", days=10, stdout=out)

    assert OrmPipelineExecution.objects.count() == 0
    assert OrmPipelineResult.objects.count() == 0
    assert OrmTaskExecution.objects.count() == 0
    assert OrmTaskResult.objects.count() == 0
    assert PipelineLog.objects.count() == 0


def test_clear_tasks_and_logs__non_deleted():
    today = now().today()

    pipeline_execution = baker.make_recipe(
        "pipelines.fake_pipeline_execution", run_id="123", started=today
    )
    pipeline_result = baker.make_recipe(
        "pipelines.fake_pipeline_result", execution=pipeline_execution
    )
    task_execution = baker.make_recipe(
        "pipelines.fake_task_execution", pipeline_result=pipeline_result
    )
    baker.make_recipe(
        "pipelines.fake_task_result", execution=task_execution, _quantity=3
    )
    baker.make_recipe("pipelines.fake_pipeline_log", run_id="123", _quantity=3)

    out = StringIO()
    call_command("clear_tasks_and_logs", days=10, stdout=out)

    assert OrmPipelineExecution.objects.count() == 1
    assert OrmPipelineResult.objects.count() == 1
    assert OrmTaskExecution.objects.count() == 1
    assert OrmTaskResult.objects.count() == 3
    assert PipelineLog.objects.count() == 3


def test_clear_tasks_and_logs__part_deleted(freezer):
    today = now().today()

    for d in [9, 11]:
        freezer.move_to(today - timedelta(days=d))

        pipeline_execution = baker.make_recipe(
            "pipelines.fake_pipeline_execution", started=now().today()
        )
        pipeline_result = baker.make_recipe(
            "pipelines.fake_pipeline_result", execution=pipeline_execution
        )
        task_execution = baker.make_recipe(
            "pipelines.fake_task_execution", pipeline_result=pipeline_result
        )
        baker.make_recipe(
            "pipelines.fake_task_result", execution=task_execution, _quantity=2
        )
        baker.make_recipe(
            "pipelines.fake_pipeline_log", run_id=pipeline_execution.run_id, _quantity=2
        )

    freezer.move_to(today)

    out = StringIO()
    call_command("clear_tasks_and_logs", days=10, stdout=out)

    assert OrmPipelineResult.objects.count() == 1
    assert OrmTaskResult.objects.count() == 2
    assert PipelineLog.objects.count() == 2

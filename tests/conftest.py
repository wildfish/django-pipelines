from itertools import chain

import pytest

from pipelines.registry import pipeline_registry
from pipelines.results.helpers import reset_storage_object
from pipelines.tasks.registry import task_registry
from tests.pipelines.app import pipelines


@pytest.fixture(autouse=True)
def auto_pipeline_registry():
    pipeline_registry.reset()
    pipeline_registry.register(pipelines.TestPipeline)
    pipeline_registry.register(pipelines.TestModelPipeline)
    pipeline_registry.register(pipelines.TestIteratorPipeline)
    pipeline_registry.register(pipelines.TestModelPipelineQS)


@pytest.fixture(autouse=True)
def auto_task_registry():
    task_registry.reset()
    for task in chain(
        pipelines.TestPipeline.tasks.values(),
        pipelines.TestModelPipeline.tasks.values(),
        pipelines.TestIteratorPipeline.tasks.values(),
        pipelines.TestModelPipelineQS.tasks.values(),
    ):
        task_registry.register(type(task))


@pytest.fixture(autouse=True)
def reset_pipeline_storage_class():
    reset_storage_object()

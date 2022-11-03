import pytest

from datorum.pipelines.tasks.registry import task_registry


@pytest.fixture(autouse=True)
def reset_registry():
    task_registry.reset()
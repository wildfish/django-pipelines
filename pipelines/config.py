from typing import TYPE_CHECKING

from django.conf import settings
from django.utils.module_loading import import_string


if TYPE_CHECKING:  # pragma: nocover
    from pipelines.runners import PipelineRunner


def object_from_config(reporter):
    if isinstance(reporter, str):
        return import_string(reporter)()

    module_path, params = reporter
    return import_string(module_path)(**params)


class Config:
    """
    Class for resolving settings related to pipelines
    """

    @property
    def PIPELINES_DEFAULT_PIPELINE_RUNNER(cls) -> "PipelineRunner":
        """
        The pipeline runner to use by default
        """
        runner = getattr(
            settings,
            "PIPELINES_PIPELINE_RUNNER",
            "pipelines.runners.eager.Runner",
        )
        return object_from_config(runner)

    @property
    def PIPELINES_DEFAULT_PIPELINE_REPORTER(cls):
        """
        The pipeline reporter to use by default
        """
        reporter = getattr(
            settings,
            "PIPELINES_PIPELINE_REPORTER",
            (
                "pipelines.reporters.base.MultiPipelineReporter",
                {
                    "reporters": [
                        "pipelines.reporters.logging.LoggingReporter",
                        "pipelines.reporters.orm.ORMReporter",
                    ]
                },
            ),
        )
        return object_from_config(reporter)

    @property
    def PIPELINES_CLEAR_LOG_DAYS(cls):
        """
        The maximum age of logs when ``clear_tasks_and_logs`` is called if no maximum
        age is specified.
        """
        days = getattr(
            settings,
            "PIPELINES_CLEAR_LOG_DAYS",
            30,
        )
        return days

    @property
    def PIPELINES_DEFAULT_PIPELINE_STORAGE(self):
        """
        The default storage class to use when storing task results
        """
        storage = getattr(
            settings,
            "PIPELINES_PIPELINES_RESULTS_STORAGE",
            "pipelines.results.orm.OrmPipelineResultsStorage",
        )
        return object_from_config(storage)

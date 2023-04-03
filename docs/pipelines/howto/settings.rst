Settings
========

PIPELINES_DEFAULT_PIPELINE_RUNNER
---------------------------------

A python path to the runner to use.

**default** :code:`pipelines.runners.eager.Runner`

PIPELINES_DEFAULT_PIPELINE_REPORTER
-----------------------------------

Either a python path to the reporter to use or a 2-tuple where the
first element is the python path to the reporter and the second is
a dictionary of keyword arguments to pass to the reporter on
construction.

**default**::

    (
        "pipelines.reporters.base.MultiPipelineReporter",
        {
            "reporters": [
                "pipelines.reporters.logging.LoggingReporter",
                "pipelines.reporters.orm.ORMReporter",
            ]
        },
    )

PIPELINES_CLEAR_LOG_DAYS
------------------------

The default number of days to use when clearing the logs.

**default** :code:`30`

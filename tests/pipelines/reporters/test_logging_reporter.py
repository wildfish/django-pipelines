import logging
from unittest.mock import Mock

import pytest

from pipelines.reporters.logging import LoggingReporter
from pipelines.status import PipelineTaskStatus


pytestmark = pytest.mark.django_db


def test_report_writes_the_message_to_info(caplog):
    caplog.set_level(logging.INFO)

    LoggingReporter().report(
        Mock(),
        PipelineTaskStatus.DONE,
        "The Message",
    )

    assert "The Message" in caplog.text

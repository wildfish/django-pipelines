import re
import uuid

from django.contrib.auth.mixins import AccessMixin
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.views.generic import FormView, ListView, TemplateView
from django.views.generic.base import RedirectView

from pipelines import config
from pipelines.forms import LogFilterForm, PipelineStartForm
from pipelines.log import logger
from pipelines.registry import pipeline_registry
from pipelines.results.helpers import (
    get_pipeline_digest,
    get_pipeline_execution,
    get_pipeline_executions,
    get_task_result,
)
from pipelines.runners.celery.tasks import run_pipeline, run_task
from pipelines.runners.eager import Runner as EagerRunner
from pipelines.status import PipelineTaskStatus


class IsStaffRequiredMixin(AccessMixin):
    """
    Verify that the current user is_staff.

    If the user is not staff the view will return the result of ``handle_no_permission``
    otherwise the views usual ``dispatch`` method will be called.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class PipelineListView(IsStaffRequiredMixin, TemplateView):
    """
    Renders a list of all registered pipelines along with their running stats.
    """

    template_name = "pipelines/pipeline_list.html"

    def get_context_data(self, **kwargs):
        digest = get_pipeline_digest()

        return {
            **super().get_context_data(**kwargs),
            "runs": {k: v.total_runs for k, v in digest.items()},
            "failed": {k: v.total_failure for k, v in digest.items()},
            "last_ran": {k: v.last_ran for k, v in digest.items()},
            "average_runtime": {k: v.average_runtime for k, v in digest.items()},
            "pipelines": pipeline_registry.items,
        }


class PipelineExecutionListView(IsStaffRequiredMixin, ListView):
    """
    Renders a list of all ``PipelineExecution``s for a given pipeline.

    :params slug: The id of the pipeline to fetch executions for.
    """

    template_name = "pipelines/pipeline_execution_list.html"
    paginate_by = 30

    def get_queryset(self):
        return get_pipeline_executions(pipeline_id=self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "slug": self.kwargs["slug"],
        }


class PipelineStartView(IsStaffRequiredMixin, FormView):
    """
    Renders a form to start a pipeline running. If there is any input data required
    by any of the tasks, a form will be rendered to allow the user to pass values to
    the pipeline.

    :params slug: The id of the pipeline to fetch executions for.
    """

    template_name = "pipelines/pipeline_start.html"
    form_class = PipelineStartForm

    def get_context_data(self, **kwargs):
        pipeline_cls = pipeline_registry.get_by_id(self.kwargs["slug"])
        tasks = list(pipeline_cls.tasks.items())
        return {
            **super().get_context_data(**kwargs),
            "pipeline": pipeline_cls,
            "tasks": tasks,
        }

    def get_form_kwargs(self):
        pipeline_cls = pipeline_registry.get_by_id(self.kwargs["slug"])

        return {
            **super().get_form_kwargs(),
            "pipeline_cls": pipeline_cls,
        }

    def form_valid(self, form):
        # generate an id for the new run
        self.run_id = str(uuid.uuid4())

        # are we starting it straight away or passing it off to celery to start
        if isinstance(config.Config().PIPELINES_DEFAULT_PIPELINE_RUNNER, EagerRunner):
            logger.debug("running pipeline in eager")
            # trigger in eager
            pipeline_cls = pipeline_registry.get_by_id(self.kwargs["slug"])
            runner = EagerRunner()
            reporter = config.Config().PIPELINES_DEFAULT_PIPELINE_REPORTER

            pipeline_cls().start(
                run_id=self.run_id,
                input_data=form.cleaned_data,
                runner=runner,
                reporter=reporter,
            )
        else:
            logger.debug("running pipeline in celery")
            # trigger in celery
            run_pipeline.delay(
                pipeline_id=self.kwargs["slug"],
                input_data=form.cleaned_data,
                run_id=self.run_id,
            )

        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("pipelines:results", args=(self.run_id,))


class PipelineResultView(IsStaffRequiredMixin, TemplateView):
    """
    Shows the results for a given pipeline run.

    :param run_id: The id of the run to view.
    """

    template_name = "pipelines/results_list.html"


class TaskResultListView(IsStaffRequiredMixin, ListView):
    """
    View to return the rendered task results view. This is intended to be polled
    by htmx to render the results list content.

    It will return with a status code of 200 unless the pipeline execution has
    complete at which point it will resturn with a status code of 286 instructing
    htmx to stop polling.

    :param run_id: The id of the run to view.
    """

    template_name = "pipelines/_results_list.html"

    @cached_property
    def pipeline_execution(self):
        pe = get_pipeline_execution(self.kwargs["run_id"])
        if not pe:
            raise Http404()

        return pe

    def get_queryset(self):
        return self.pipeline_execution.get_pipeline_results()

    def all_tasks_completed(self):
        return (
            self.pipeline_execution.get_status() in PipelineTaskStatus.final_statuses()
        )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        #  286 status stops htmx from polling
        response.status_code = 286 if self.all_tasks_completed() else 200
        return response


class LogListView(IsStaffRequiredMixin, TemplateView):
    """
    View to return the rendered logs for the selected context item. . This is intended
    to be polled by htmx to render the results list content.

    The logs can be filtered by passing 2 query string parameters:

    * ``type``: One of "PipelineResult", "TaskExecution" or "TaskResult".
    * ``id``: The id of the object in the results storage.

    It will return with a status code of 200 unless the pipeline execution has
    complete at which point it will resturn with a status code of 286 instructing
    htmx to stop polling.

    :param run_id: The id of the run to view.
    """

    template_name = "pipelines/_log_list.html"

    @cached_property
    def pipeline_execution(self):
        pe = get_pipeline_execution(self.kwargs["run_id"])
        if not pe:
            raise Http404()

        return pe

    def all_tasks_completed(self):
        return (
            self.pipeline_execution.get_status() in PipelineTaskStatus.final_statuses()
        )

    def _get_orm_logs(self, run_id):
        form = LogFilterForm(self.request.GET)

        logs = (
            form.qs.filter(run_id=run_id)
            .order_by("created")
            .values_list("created", "message")
        )

        return "\n".join(
            [f"[{log[0].strftime('%d/%b/%Y %H:%M:%S')}]: {log[1]}" for log in logs]
        )

    def get_logs(self, run_id):
        logs = self._get_orm_logs(run_id=run_id)

        return logs

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        #  286 status stops htmx from polling
        response.status_code = 286 if self.all_tasks_completed() else 200
        return response

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "logs": self.get_logs(kwargs["run_id"]),
        }


class LogFilterView(IsStaffRequiredMixin, TemplateView):
    """
    View that updates the htmx log view to include filter parameters.

    ``filter`` should be applied as a query parameter. The value should
    be the the type and id of the object to fetch logs for. For example
    ``filter=PipelineResult-1`` will filter log by the ``PipelineResult``
    with id 1.

    :param run_id: The id of the run to view.
    """

    template_name = "pipelines/_log_filter.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, log_url=self.log_url)

    @property
    def log_url(self):
        filter_qs = self.request.GET.get("filter", "")
        filter_qs_match = re.match(r"(.+)-(\d+)", filter_qs)

        if filter_qs_match:
            filter_name = filter_qs_match.group(1)
            filter_value = filter_qs_match.group(2)

            return (
                reverse("pipelines:logs-list", kwargs=self.kwargs)
                + f"?type={filter_name}&id={filter_value}"
            )
        else:
            return reverse("pipelines:logs-list", kwargs=self.kwargs)


class TaskResultReRunView(IsStaffRequiredMixin, RedirectView):
    """
    View to rerun a specific task.

    :param pk: The id of the task result to rerun.
    """

    def get_object(self, queryset=None):
        tr = get_task_result(self.kwargs["pk"])
        if not tr:
            raise Http404()

        return tr

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        task = self.object.get_task()
        if task is None:
            raise Http404()

        # start the task again
        #
        # TODO: Add a method to run a single task to the runner so we dont need to do this
        # check as it will fall down for custom runners
        #
        if isinstance(config.Config().PIPELINES_DEFAULT_PIPELINE_RUNNER, EagerRunner):
            run_task(
                task_id=self.object.get_task_id(),
                run_id=self.object.get_run_id(),
                pipeline_id=self.object.get_pipeline_id(),
                input_data=self.object.get_input_data(),
                serializable_pipeline_object=self.object.get_serializable_pipeline_object(),
                serializable_task_object=self.object.get_serializable_task_object(),
            )
        else:
            run_task.delay(
                task_id=self.object.get_task_id(),
                run_id=self.object.get_run_id(),
                pipeline_id=self.object.get_pipeline_id(),
                input_data=self.object.get_input_data(),
                serializable_pipeline_object=self.object.get_serializable_pipeline_object(),
                serializable_task_object=self.object.get_serializable_task_object(),
            )

        response = super().get(request, *args, **kwargs)
        return response

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("pipelines:results", args=(self.object.get_run_id(),))

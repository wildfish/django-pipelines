from typing import TYPE_CHECKING, Dict

from django.utils.module_loading import autodiscover_modules

from datorum.pipelines.log import logger


if TYPE_CHECKING:  # pragma: no cover
    from .base import BasePipeline


class RegistryError(Exception):
    pass


class PipeLineRegistry(object):
    def __init__(self):
        self.pipelines: Dict[str, BasePipeline] = {}  #

    def autodiscover_pipelines(self, module_name="pipelines"):
        autodiscover_modules(module_name)

    def register(self, cls):
        slug = self.get_slug(cls.__module__, cls.__name__)
        if slug in self.pipelines:
            raise RegistryError(f"Multiple pipelines with {slug} have been registered.")

        logger.debug(f"registering pipeline {slug}")
        self.pipelines[slug] = cls

    def get_all_registered_pipelines(self):
        return list(self.pipelines.values())

    def get_all_registered_pipeline_ids(self):
        return self.pipelines.keys()

    def get_pipeline_class(self, slug):
        if slug in self.pipelines:
            return self.pipelines[slug]
        return None

    def get_slug(self, module, class_name):
        return "{}.{}".format(module, class_name)


pipeline_registry = PipeLineRegistry()
import abc
from functools import cached_property, lru_cache
from typing import Optional

from overhave.factory import IOverhaveFactory
from overhave.pytest_plugin.config_injector import ConfigInjector
from overhave.pytest_plugin.plugin_resolver import PluginResolver


class IProxyManager:
    """ Abstract class for proxy manager. """

    @property
    @abc.abstractmethod
    def injector(self) -> ConfigInjector:
        pass

    @abc.abstractmethod
    def set_factory(self, factory: IOverhaveFactory):
        pass

    @property
    @abc.abstractmethod
    def factory(self):
        pass

    @property
    @abc.abstractmethod
    def has_factory(self) -> bool:
        pass

    @abc.abstractmethod
    def patch_pytest(self) -> None:
        pass

    @property
    @abc.abstractmethod
    def plugin_resolver(self) -> PluginResolver:
        pass

    @property
    @abc.abstractmethod
    def pytest_patched(self) -> bool:
        pass

    @abc.abstractmethod
    def supply_injector_for_collection(self) -> None:
        pass


class BaseProxyManagerException(Exception):
    """ Base exception for :class:`ProxyManager`. """


class FactoryAlreadyDefinedError(BaseProxyManagerException):
    """ Exception for situation with already defined `factory`. """


class FactoryNotDefinedError(BaseProxyManagerException):
    """ Exception for situation with not defined `factory`. """


class ProxyManager(IProxyManager):
    """ Manager for application factory resolution and usage, based on proxy-object pattern. """

    def __init__(self) -> None:
        self._factory: Optional[IOverhaveFactory] = None
        self._pytest_patched = False
        self._collection_prepared = False

    @cached_property
    def _injector(self) -> ConfigInjector:
        return ConfigInjector()

    @property
    def injector(self) -> ConfigInjector:
        return self._injector

    def set_factory(self, factory: IOverhaveFactory):
        if self._factory is not None:
            raise FactoryAlreadyDefinedError("Factory is not nullable!")
        self._factory = factory

    @property
    def factory(self):
        if self._factory is None:
            raise FactoryNotDefinedError("Factory is nullable!")
        return self._factory

    @property
    def has_factory(self) -> bool:
        return self._factory is not None

    def patch_pytest(self) -> None:
        if not self._pytest_patched:
            self._injector.patch_pytestbdd_prefixes(
                custom_step_prefixes=self._factory.context.language_settings.step_prefixes
            )
            self._pytest_patched = True

    @cached_property
    def _plugin_resolver(self) -> PluginResolver:
        return PluginResolver(self._factory.context.file_settings)

    @property
    def plugin_resolver(self) -> PluginResolver:
        return self._plugin_resolver

    @property
    def pytest_patched(self) -> bool:
        return self._pytest_patched

    def supply_injector_for_collection(self) -> None:
        if not self._collection_prepared:
            self._injector.supplement_components(
                file_settings=self._factory.context.file_settings,
                step_collector=self._factory.step_collector,
                test_runner=self._factory.test_runner,
                feature_extractor=self._factory.feature_extractor,
            )
            self._collection_prepared = True


@lru_cache(maxsize=None)
def get_proxy_manager() -> IProxyManager:
    return ProxyManager()
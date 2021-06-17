from copy import deepcopy
from functools import cached_property
from pathlib import Path
from typing import Dict

from pydantic import BaseSettings

from overhave import (
    OverhaveAdminSettings,
    OverhaveFileSettings,
    OverhaveLanguageSettings,
    OverhaveStashClientSettings,
    OverhaveStashPublisherSettings,
)
from overhave.extra import RUSSIAN_PREFIXES
from overhave.publication.gitlab import OverhaveGitlabPublisherSettings
from overhave.publication.objects import PublicationManagerType
from overhave.publication.settings import PublicationSettings
from overhave.transport import OverhaveGitlabClientSettings


class OverhaveDemoSettingsGenerator:
    """ Settings for application demo mode configuration. """

    root_dir: Path = Path(__file__).parent

    @cached_property
    def default_context_settings(self) -> Dict[str, BaseSettings]:
        return dict(
            language_settings=OverhaveLanguageSettings(step_prefixes=RUSSIAN_PREFIXES),
            file_settings=OverhaveFileSettings(root_dir=self.root_dir.as_posix()),
        )

    def get_admin_context_settings(self, threadpool: bool) -> Dict[str, BaseSettings]:
        settings: Dict[str, BaseSettings] = dict(admin_settings=OverhaveAdminSettings(consumer_based=not threadpool))
        settings.update(self.default_context_settings)
        return settings

    @cached_property
    def publication_settings(self) -> Dict[str, BaseSettings]:
        settings = deepcopy(self.default_context_settings)
        if PublicationSettings().publication_manager_type == PublicationManagerType.GITLAB:
            repository_id: str = "2034"
            settings["publisher_settings"] = OverhaveGitlabPublisherSettings(repository_id=repository_id)
            settings["client_settings"] = OverhaveGitlabClientSettings(
                url="https://overhave.readthedocs.io/not-a-handler",
                auth_token="secret_token",
                repository_id=repository_id,
            )
            return settings
        settings["client_settings"] = OverhaveStashClientSettings(
            url="https://overhave.readthedocs.io/not-a-handler", auth_token="secret_token"
        )
        settings["publisher_settings"] = OverhaveStashPublisherSettings(
            repository_name="bdd-features", project_key="OVH"
        )
        return settings

from __future__ import annotations

import importlib
import sys
import warnings


def import_fresh(module_name: str):
    for loaded_name in list(sys.modules):
        if loaded_name == module_name or loaded_name.startswith(f"{module_name}."):
            sys.modules.pop(loaded_name)
    return importlib.import_module(module_name)


def test_canonical_package_exports_public_surface():
    import linkedin_web_scraper
    from linkedin_web_scraper.application.linkedin_job_scraper import LinkedInJobScraper
    from linkedin_web_scraper.config.job_scraper_config import JobScraperConfig
    from linkedin_web_scraper.infra.logging import Logger

    assert linkedin_web_scraper.LinkedInJobScraper is LinkedInJobScraper
    assert linkedin_web_scraper.JobScraperConfig is JobScraperConfig
    assert linkedin_web_scraper.Logger is Logger


def test_legacy_package_import_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        module = import_fresh("LinkedInWebScraper")

    assert module.LinkedInJobScraper.__module__.startswith("linkedin_web_scraper")
    assert any("`LinkedInWebScraper` is deprecated" in str(warning.message) for warning in caught)


def test_legacy_submodules_reexport_canonical_symbols():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        legacy_config = import_fresh("LinkedInWebScraper.job_scraper_config")
        legacy_file_manager = import_fresh("Utils.file_manager")
        legacy_openai_handler = import_fresh("OpenAIHandler.openai_handler")

    from linkedin_web_scraper.config.job_scraper_config import JobScraperConfig
    from linkedin_web_scraper.infra.openai.openai_handler import OpenAIHandler
    from linkedin_web_scraper.infra.storage.file_manager import FileManager

    assert legacy_config.JobScraperConfig is JobScraperConfig
    assert issubclass(legacy_file_manager.FileManager, FileManager)
    assert legacy_openai_handler.OpenAIHandler is OpenAIHandler
    assert any("LinkedInWebScraper.job_scraper_config" in str(warning.message) for warning in caught)
    assert any("Utils.file_manager" in str(warning.message) for warning in caught)
    assert any("OpenAIHandler.openai_handler" in str(warning.message) for warning in caught)


def test_constant_exports_stay_aligned_across_namespaces():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        legacy_constants = import_fresh("Utils.constants")

    from linkedin_web_scraper.config import (
        LOCATION_MAPPING as config_location_mapping,
    )
    from linkedin_web_scraper.config import (
        USER_AGENT_HEADERS as config_user_agent_headers,
    )
    from linkedin_web_scraper.config.constants import (
        LOCATION_MAPPING as constants_location_mapping,
    )
    from linkedin_web_scraper.config.constants import (
        USER_AGENT_HEADERS as constants_user_agent_headers,
    )

    assert legacy_constants.LOCATION_MAPPING == config_location_mapping == constants_location_mapping
    assert (
        legacy_constants.USER_AGENT_HEADERS
        == config_user_agent_headers
        == constants_user_agent_headers
    )
    assert not hasattr(legacy_constants, "normalize_location_name")
    assert any("Utils.constants" in str(warning.message) for warning in caught)

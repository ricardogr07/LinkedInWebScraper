from __future__ import annotations

import logging

import pandas as pd
import pytest

from linkedin_web_scraper.infra.anthropic.anthropic_handler import (
    AnthropicConfigurationError,
    AnthropicHandler,
)
from linkedin_web_scraper.infra.openai.job_description_processor import JobDescriptionProcessor
from linkedin_web_scraper.infra.openai.models import JobDescriptionEnrichment

LOGGER = logging.getLogger("test-anthropic-enrichment")
LOGGER.handlers.clear()
LOGGER.addHandler(logging.NullHandler())


class FakeParsedPayload:
    def __init__(self, payload: dict[str, object]):
        self.payload = payload

    def model_dump(self, mode: str = "json") -> dict[str, object]:
        assert mode == "json"
        return dict(self.payload)


class FakeParsedResponse:
    def __init__(
        self,
        payload: dict[str, object],
        *,
        response_id: str = "msg_123",
        model: str = "claude-haiku-4-5-20251001",
    ):
        self.id = response_id
        self.model = model
        self.parsed_output = FakeParsedPayload(payload)


class FakeMessagesAPI:
    def __init__(self, response: FakeParsedResponse):
        self.response = response
        self.last_kwargs: dict[str, object] | None = None

    def parse(self, **kwargs):
        self.last_kwargs = kwargs
        return self.response


class FakeAnthropicClient:
    def __init__(self, response: FakeParsedResponse):
        self.messages = FakeMessagesAPI(response)


class FlakyEnricher:
    def __init__(self):
        self.calls: list[str] = []

    def extract_job_description(self, description: str) -> JobDescriptionEnrichment:
        self.calls.append(description)
        if "raise" in description:
            raise RuntimeError("boom")
        return JobDescriptionEnrichment(
            short_description="Short summary",
            tech_stack=("Python", "SQL"),
            years_of_experience="3+ years",
            minimum_level_of_studies="Bachelor",
            english_required=True,
            model="claude-haiku-4-5-20251001",
            response_id="msg_456",
            raw_payload={"description": "Short summary", "tech_stack": ["Python", "SQL"]},
        )


def test_anthropic_handler_extracts_structured_enrichment_from_messages_parse():
    payload = {
        "description": "Build data products.",
        "tech_stack": ["Python", "SQL"],
        "years_of_experience": "3+ years",
        "minimum_level_of_studies": "Bachelor's degree",
        "english_required": True,
    }
    client = FakeAnthropicClient(FakeParsedResponse(payload))
    handler = AnthropicHandler(client=client)

    enrichment = handler.extract_job_description("Build data products.")

    assert client.messages.last_kwargs is not None
    assert client.messages.last_kwargs["model"] == "claude-haiku-4-5-20251001"
    assert enrichment.short_description == "Build data products."
    assert enrichment.tech_stack == ("Python", "SQL")
    assert enrichment.years_of_experience == "3+ years"
    assert enrichment.minimum_level_of_studies == "Bachelor's degree"
    assert enrichment.english_required is True
    assert enrichment.model == "claude-haiku-4-5-20251001"
    assert enrichment.response_id == "msg_123"
    assert enrichment.raw_payload == payload


def test_anthropic_handler_requires_api_key_without_injected_client(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(AnthropicConfigurationError):
        AnthropicHandler()


def test_job_description_processor_works_with_anthropic_handler():
    df_jobs = pd.DataFrame(
        [
            {"JobID": "1", "Description": "works fine"},
            {"JobID": "2", "Description": "raise this one"},
            {"JobID": "3", "Description": ""},
        ]
    )
    processor = JobDescriptionProcessor(FlakyEnricher(), logger=LOGGER)

    enriched = processor.process_job_descriptions(df_jobs)

    assert enriched.loc[0, "ShortDescription"] == "Short summary"
    assert enriched.loc[0, "TechStack"] == "Python, SQL"
    assert enriched.loc[0, "YoE"] == "3+ years"
    assert enriched.loc[0, "MinLevelStudies"] == "Bachelor"
    assert enriched.loc[0, "English"] is True
    assert enriched.loc[0, "EnrichmentModel"] == "claude-haiku-4-5-20251001"
    assert enriched.loc[0, "EnrichmentResponseId"] == "msg_456"
    assert '"description": "Short summary"' in enriched.loc[0, "EnrichmentRawPayload"]

    assert enriched.loc[1, "ShortDescription"] == "N/A"
    assert enriched.loc[1, "TechStack"] == "N/A"
    assert enriched.loc[1, "EnrichmentRawPayload"] == ""

    assert enriched.loc[2, "ShortDescription"] == "N/A"
    assert enriched.loc[2, "English"] == "N/A"

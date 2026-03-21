from __future__ import annotations

import logging

import pandas as pd
import pytest

from linkedin_web_scraper.infra.openai.job_description_processor import JobDescriptionProcessor
from linkedin_web_scraper.infra.openai.models import JobDescriptionEnrichment
from linkedin_web_scraper.infra.openai.openai_handler import OpenAIConfigurationError, OpenAIHandler

LOGGER = logging.getLogger("test-openai-enrichment")
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
        response_id: str = "resp_123",
        model: str = "gpt-4o-mini",
    ):
        self.id = response_id
        self.model = model
        self.output_parsed = FakeParsedPayload(payload)


class FakeResponsesAPI:
    def __init__(self, response: FakeParsedResponse):
        self.response = response
        self.last_kwargs: dict[str, object] | None = None

    def parse(self, **kwargs):
        self.last_kwargs = kwargs
        return self.response


class FakeOpenAIClient:
    def __init__(self, response: FakeParsedResponse):
        self.responses = FakeResponsesAPI(response)


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
            model="gpt-4o-mini",
            response_id="resp_456",
            raw_payload={"description": "Short summary", "tech_stack": ["Python", "SQL"]},
        )


def test_openai_handler_extracts_structured_enrichment_from_responses_parse():
    payload = {
        "description": "Build data products.",
        "tech_stack": ["Python", "SQL"],
        "years_of_experience": "3+ years",
        "minimum_level_of_studies": "Bachelor's degree",
        "english_required": True,
    }
    client = FakeOpenAIClient(FakeParsedResponse(payload))
    handler = OpenAIHandler(client=client)

    enrichment = handler.extract_job_description("Build data products.")

    assert client.responses.last_kwargs is not None
    assert client.responses.last_kwargs["model"] == "gpt-4o-mini"
    assert enrichment.short_description == "Build data products."
    assert enrichment.tech_stack == ("Python", "SQL")
    assert enrichment.years_of_experience == "3+ years"
    assert enrichment.minimum_level_of_studies == "Bachelor's degree"
    assert enrichment.english_required is True
    assert enrichment.model == "gpt-4o-mini"
    assert enrichment.response_id == "resp_123"
    assert enrichment.raw_payload == payload


def test_openai_handler_generate_chat_completion_returns_legacy_shape():
    client = FakeOpenAIClient(
        FakeParsedResponse(
            {
                "description": "Analyze large datasets.",
                "tech_stack": ["Python", "Pandas"],
                "years_of_experience": "N/A",
                "minimum_level_of_studies": "N/A",
                "english_required": None,
            }
        )
    )
    handler = OpenAIHandler(client=client)

    result = handler.generate_chat_completion(handler.create_messages("Analyze large datasets."))

    assert result == {
        "Description": "Analyze large datasets.",
        "TechStack": ["Python", "Pandas"],
        "YoE": "N/A",
        "MinLevelStudies": "N/A",
        "English": "N/A",
    }


def test_openai_handler_requires_api_key_without_injected_client(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(OpenAIConfigurationError):
        OpenAIHandler()


def test_job_description_processor_continues_after_per_row_enrichment_failures():
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
    assert enriched.loc[0, "OpenAIModel"] == "gpt-4o-mini"
    assert enriched.loc[0, "OpenAIResponseId"] == "resp_456"
    assert '"description": "Short summary"' in enriched.loc[0, "OpenAIRawPayload"]

    assert enriched.loc[1, "ShortDescription"] == "N/A"
    assert enriched.loc[1, "TechStack"] == "N/A"
    assert enriched.loc[1, "OpenAIRawPayload"] == ""

    assert enriched.loc[2, "ShortDescription"] == "N/A"
    assert enriched.loc[2, "English"] == "N/A"

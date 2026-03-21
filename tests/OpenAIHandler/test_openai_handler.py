from __future__ import annotations

import os

import pytest


@pytest.mark.live_openai
@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY is required for live OpenAI tests"
)
def test_openai_handler_live_round_trip():
    pytest.importorskip("openai")
    pytest.importorskip("pydantic")

    from OpenAIHandler.openai_handler import OpenAIHandler

    handler = OpenAIHandler()
    enrichment = handler.extract_job_description(
        "Data Scientist role requiring Python, SQL, and strong English communication."
    )
    legacy_result = handler.generate_chat_completion(
        handler.create_messages("Data Scientist role requiring Python and SQL.")
    )

    assert enrichment.short_description != "N/A"
    assert enrichment.model is not None
    assert legacy_result["Description"] != "N/A"
    assert "TechStack" in legacy_result

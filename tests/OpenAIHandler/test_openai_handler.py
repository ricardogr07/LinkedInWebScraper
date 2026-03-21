from __future__ import annotations

import os

import pytest


@pytest.mark.live_openai
@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY is required for live OpenAI tests"
)
def test_openai_handler_live_round_trip():
    from OpenAIHandler.openai_handler import OpenAIHandler

    handler = OpenAIHandler()
    messages = handler.create_messages("Data Scientist role requiring Python and SQL.")

    result = handler.generate_chat_completion(messages)

    assert result is not None
    assert "Description" in result

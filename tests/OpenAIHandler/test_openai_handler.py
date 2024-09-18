import json
from OpenAIHandler.openai_handler import OpenAIHandler
import pytest

class TestOpenAIHandler:

    def test_openai_handler(self):
        handler = OpenAIHandler()

        job_description = (
            "The primary responsibilities of the Data Scientist include analyzing large datasets, "
            "developing predictive models, and providing actionable insights to stakeholders. "
            "Experience with Python, R, SQL, and machine learning frameworks is required."
        )

        messages = handler.create_messages(job_description)

        try:
            result = handler.generate_chat_completion(messages)
            assert result is not None, "Result should not be None"
            print("API Response:")
            print(json.dumps(result, indent=4))
        except Exception as e:
            assert False, f"An error occurred: {e}"

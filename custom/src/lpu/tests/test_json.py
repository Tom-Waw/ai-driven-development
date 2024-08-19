import pytest
from lpu.agent import DEFAULT_LLM, DEFAULT_PROMPT_FORMATTERS, Agent
from lpu.parsing.json_parser import JSONResponseParser


@pytest.fixture
def parser():
    return JSONResponseParser()


@pytest.fixture
def agent(parser):
    return Agent(
        name="TestAgent",
        llm=DEFAULT_LLM,
        prompt_formatters=DEFAULT_PROMPT_FORMATTERS,
        response_parsers=[parser],
    )


def test_json_response_parsing(agent, parser):
    expected = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
    }

    prompt = (
        "Generate a JSON representation of a single user with the following user details:"
        + f"Name: {expected['name']}, Email: {expected['email']}, Phone: {expected['phone']}"
    )

    response = agent.prompt(prompt)
    context = response["context"]

    assert parser.response_field in context
    assert len(context[parser.response_field]) == 1

    actual = context[parser.response_field][0]
    assert actual == expected

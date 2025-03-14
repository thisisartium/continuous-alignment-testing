import json

import anthropic
import openlit
from helpers import load_json_fixture
from openai import OpenAI

openlit.init()


def test_anthropic_to_opentelemetry():
    client = anthropic.Anthropic()
    assert client is not None

    responses = (
        client.messages.create(
            max_tokens=8192,
            model="claude-3-7-sonnet-20250219",
            system=system_prompt(),
            messages=[
                {"role": "user", "content": user_prompt()},
            ],
        )
        .content[0]
        .text
    )

    not_empty_response = True

    try:
        json_object = json.loads(responses)
        print(json_object)
        developer_names = {developer["name"] for developer in json_object["developers"]}
        not_empty_response = len(developer_names) != 0
    except json.JSONDecodeError as e:
        print(f"JSON Exception: {e}")

    assert not_empty_response


def test_openai_to_opentelemetry():
    client = OpenAI()
    assert client is not None

    responses = (
        client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": system_prompt()},
                {"role": "user", "content": user_prompt()},
            ],
            response_format={"type": "json_object"},
        )
        .choices[0]
        .message.content
    )

    not_empty_response = True

    try:
        json_object = json.loads(responses)
        developer_names = {developer["name"] for developer in json_object["developers"]}
        not_empty_response = len(developer_names) != 0
    except json.JSONDecodeError as e:
        print(f"JSON Exception: {e}")

    assert not_empty_response


def system_prompt():
    skills_data = load_json_fixture("skills.json")
    example_output = load_json_fixture("example_output.json")

    system_prompt = f"""
        You will get a description of a project, and your task is
        to tell me the best developers from the given list for the project based on their skills.
        Today's date is April 15th, 2025.
        Pick only developers who are available after the project start date.
        Pick people with higher skill levels first.
        Respond in json with this structure:
            {example_output}

        Here is the skills data:
        """

    return system_prompt + str(skills_data)


def user_prompt():
    return """
    This is a mobile project for telecommunication company. The project starts June 3rd.
    It will find exciting moments from sports highlights videos.
    """

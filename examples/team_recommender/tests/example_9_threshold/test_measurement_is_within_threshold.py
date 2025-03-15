import json
from typing import List

import openai
from helpers import is_within_expected, load_json_fixture
from openai import OpenAI
from openai.types.chat.chat_completion import Choice
from response_matches_json_schema import response_matches_json_schema
from retry import retry
from settings import root_dir

from cat_ai.reporter import Reporter
from cat_ai.runner import Runner


def get_all_developer_names(skills_data) -> set[str]:
    return {
        developer["developer"]["name"]
        for skill in skills_data["skills"]
        for developer in skill["developerSkills"]
    }


def get_developer_names_from_response(response) -> set[str]:
    return {developer["name"] for developer in response["developers"]}


def test_response_matches_json_schema():
    # Load example output and schema
    example_output = load_json_fixture("example_output.json")
    schema = load_json_fixture("output_schema.json")

    assert response_matches_json_schema(example_output, schema)


def test_metrics_within_range():
    generations = Runner.get_sample_size()

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
    system_prompt = system_prompt + str(skills_data)

    project_description = """
    This is a mobile project for telecommunication company. The project starts June 3rd.
    It will find exciting moments from sports highlights videos.
    """

    responses = generate_choices(generations, project_description, system_prompt)

    results = []
    for run in range(0, generations):
        response = responses[run].message.content
        suffix = "" if generations == 1 else "s"
        test_reporter = Reporter(
            f"test_metrics_{generations}_generation{suffix}",
            metadata={
                "system_prompt": system_prompt,
                "user_prompt": project_description,
            },
            output_dir=root_dir(),
        )
        test_runner = Runner(
            lambda reporter, content=response: run_allocation_test(
                reporter, skills_data=skills_data, response=content
            ),
            reporter=test_reporter,
        )
        results.append(test_runner.run_once(run))

    expected_success_rate_measured = 0.97
    failure_count = sum(not result for result in results)
    sample_size = len(results)
    assert is_within_expected(expected_success_rate_measured, failure_count, sample_size), (
        f"Expected {expected_success_rate_measured} to be within of the success rate"
    )


@retry(
    max_attempts=4,
    exceptions=(openai.APIConnectionError,),
    initial_delay=10,
    backoff_factor=2.0,
    logger_name="openai.api",
)
def generate_choices(generations, project_description, system_prompt) -> List[Choice]:
    client = OpenAI()
    assert client is not None

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": project_description},
        ],
        response_format={"type": "json_object"},
        n=generations,
    )
    responses = completion.choices
    return responses


def run_allocation_test(reporter: Reporter, skills_data, response: str) -> bool:
    acceptable_people = ["Sam Thomas", "Drew Anderson", "Alex Wilson", "Alex Johnson"]
    all_developers = get_all_developer_names(skills_data)

    schema = load_json_fixture("output_schema.json")
    has_valid_json_schema = False

    not_empty_response = True
    no_developer_name_is_hallucinated = True
    developer_is_appropriate = True
    json_object = {}
    try:
        json_object = json.loads(response)
        has_valid_json_schema = response_matches_json_schema(json_object, schema)
        developer_names = get_developer_names_from_response(json_object)
        not_empty_response = len(developer_names) != 0
        developer_is_appropriate = any(name in developer_names for name in acceptable_people)
        if not not_empty_response:
            no_developer_name_is_hallucinated = False not in [
                name in all_developers for name in developer_names
            ]
    except json.JSONDecodeError as e:
        print(f"JSON Exception: {e}")

    reporter.report(
        json_object,
        {
            "correct_developer_suggested": developer_is_appropriate,
            "no_developer_name_is_hallucinated": no_developer_name_is_hallucinated,
            "not_empty_response": not_empty_response,
            "valid_json_returned": has_valid_json_schema,
        },
    )
    return (
        developer_is_appropriate
        and no_developer_name_is_hallucinated
        and not_empty_response
        and has_valid_json_schema
    )

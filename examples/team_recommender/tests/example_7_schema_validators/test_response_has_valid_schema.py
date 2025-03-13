import json
import os

from helpers import load_json_fixture
from jsonschema import FormatChecker, validate
from openai import OpenAI
from settings import ROOT_DIR

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


def response_matches_json_schema(response: str, schema: any) -> bool:
    """
    Validates if a given response matches the provided JSON schema.

    :param response: The response JSON data as a string.
    :param schema: The schema to validate against.
    :return: True if the response matches the schema, otherwise False.
    """
    try:
        validate(instance=response, schema=schema, format_checker=FormatChecker())
        return True
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def load_json_fixture(file_name: str) -> dict:
    """
    Utility function to load a JSON fixture file.

    :param file_name: Name of the JSON file to load.
    :return: Parsed JSON data as a dictionary.
    """
    json_path = os.path.join(ROOT_DIR, "tests/fixtures", file_name)
    with open(json_path, "r") as file:
        return json.load(file)


def test_response_matches_json_schema():
    # Load example output and schema
    example_output = load_json_fixture("example_output.json")
    schema = load_json_fixture("output_schema.json")

    assert response_matches_json_schema(example_output, schema)


def has_expected_success_rate(results: list[bool], expected_success_rate: float) -> bool:
    if not results:
        return True

    failure_count = sum(not result for result in results)
    total_count = len(results)
    failure_rate = float(failure_count) / float(total_count)
    print(1.0 - failure_rate)
    return expected_success_rate <= (1.0 - failure_rate)


def test_response_has_valid_schema():
    generations = Runner.get_sample_size()

    skills_data = load_json_fixture("skills.json")
    example_output = load_json_fixture("example_output.json")

    system_prompt = f"""
        You will get a description of a project, and your task is to tell me the best developers from the given list for the project
         based on their skills.
        Today's date is April 15th, 2025.
        Pick only developers who are available after the project start date. Pick people with higher skill levels first.
        respond in json with this structure:
            {example_output}

        Here is the skills data:
        """
    system_prompt = system_prompt + str(skills_data)

    project_description = """
    This is a mobile project for telecommunication company. The project starts June 3rd.
    It will find exciting moments from sports highlights videos.
    """

    client = OpenAI()
    assert client is not None

    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": project_description},
        ],
        response_format={"type": "json_object"},
        n=generations,
    )
    responses = completion.choices

    results = []
    for run in range(0, generations):
        response = responses[run].message.content
        test_reporter = Reporter(
            "test_fast_with_n_generations",
            metadata={
                "system_prompt": system_prompt,
                "user_prompt": project_description,
            },
            output_dir=ROOT_DIR,
        )
        test_runner = Runner(
            lambda reporter: run_allocation_test(
                reporter, skills_data=skills_data, response=response
            ),
            reporter=test_reporter,
        )
        results.append(test_runner.run_once(run))

    failure_threshold = 0.8
    assert has_expected_success_rate(results, failure_threshold)


def run_allocation_test(reporter, skills_data, response) -> bool:
    acceptable_people = ["Sam Thomas", "Drew Anderson", "Alex Wilson", "Alex Johnson"]
    all_developers = get_all_developer_names(skills_data)

    schema = load_json_fixture("output_schema.json")
    has_valid_json_schema = False

    not_empty_response = True
    no_developer_name_is_hallucinated = True
    developer_is_appropriate = True
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

import json
<<<<<<<< HEAD:examples/team_recommender/tests/example_9_threshold/test_measurement_is_within_threshold.py
import re
from typing import List
|||||||| parent of 8802138 (Add `openlit` example):examples/team_recommender/tests/example_9_retry_with_open_telemetry/test_retry_to_open_telemetry.py
from typing import List
========
>>>>>>>> 8802138 (Add `openlit` example):examples/openlit/tests/example_1_openlit_integration/test_results_available_in_openlit.py

from helpers import load_json_fixture
from jsonschema import FormatChecker, validate
from openai import OpenAI
from settings import ROOT_DIR

from cat_ai import analyse_sample_from_test
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


def test_response_matches_json_schema():
    # Load example output and schema
    example_output = load_json_fixture("example_output.json")
    schema = load_json_fixture("output_schema.json")

    assert response_matches_json_schema(example_output, schema)


def is_within_a_range(value, left, right):
    return left <= value <= right


<<<<<<<< HEAD:examples/team_recommender/tests/example_9_threshold/test_measurement_is_within_threshold.py
def test_is_within_expected():
    assert is_within_expected(0.8, 0, 5)
    assert is_within_expected(0.8, 2, 5)
    assert not is_within_expected(0.8, 3, 5)
    assert not is_within_expected(0.8, 4, 5)
    assert not is_within_expected(0.8, 5, 5)
    assert is_within_expected(0.8, 26, 100)
    assert is_within_expected(0.8, 14, 100)


def is_within_expected(success_rate: float, failure_count: int, sample_size: int):
    success_portion = int(success_rate * sample_size)
    success_analysis = analyse_sample_from_test(success_portion, sample_size)
    return is_within_a_range(
        sample_size - failure_count,
        success_analysis.confidence_interval_count[0],
        success_analysis.confidence_interval_count[1],
    )


def test_success_rate():
    tiny_set_analysis = analyse_sample_from_test(1, 2)
    assert tiny_set_analysis.proportion == 0.5
    interval = tiny_set_analysis.confidence_interval_prop

    assert interval[0] <= 0 and interval[1] >= 1, (
        f"interval includes all possible values: {interval} does not contain [0, 1]"
    )


def natural_sort_key(s):
    """Sort strings with embedded numbers in natural order."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)]


def test_sort_names_with_numbers():
    unsorted = [
        "example_1_text_response",
        "example_10_threshold",
        "example_2_unit",
        "example_8_retry_network",
        "example_9_retry_with_open_telemetry",
    ]
    incorrectly_sorted = [
        "example_10_threshold",
        "example_1_text_response",
        "example_2_unit",
        "example_8_retry_network",
        "example_9_retry_with_open_telemetry",
    ]
    assert incorrectly_sorted == sorted(unsorted)

    correctly_sorted = [
        "example_1_text_response",
        "example_2_unit",
        "example_8_retry_network",
        "example_9_retry_with_open_telemetry",
        "example_10_threshold",
    ]
    assert correctly_sorted == sorted(unsorted, key=natural_sort_key)


def test_metrics_within_range():
|||||||| parent of 8802138 (Add `openlit` example):examples/team_recommender/tests/example_9_retry_with_open_telemetry/test_retry_to_open_telemetry.py
def test_open_telemetry_receives_message():
========
def test_response_has_valid_schema():
>>>>>>>> 8802138 (Add `openlit` example):examples/openlit/tests/example_1_openlit_integration/test_results_available_in_openlit.py
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

<<<<<<<< HEAD:examples/team_recommender/tests/example_9_threshold/test_measurement_is_within_threshold.py
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

    failure_threshold = 0.9
    assert generations <= 1 or is_within_expected(
        failure_threshold, sum(not result for result in results), generations
    ), f"Expected {failure_threshold} to be within the confidence interval of the success rate"


@retry(
    max_attempts=4,
    exceptions=(openai.APIConnectionError,),
    initial_delay=10,
    backoff_factor=2.0,
    logger_name="openai.api",
)
def generate_choices(generations, project_description, system_prompt) -> List[Choice]:
|||||||| parent of 8802138 (Add `openlit` example):examples/team_recommender/tests/example_9_retry_with_open_telemetry/test_retry_to_open_telemetry.py
    retry_logger = configure_logger_for_opentelemetry("openai.api")
    retry_logger.debug("Prepared to retry generate_choices")
    responses = generate_choices(generations, project_description, system_prompt)

    results = []
    for run in range(0, generations):
        response = responses[run].message.content
        test_reporter = Reporter(
            f"test_retries_{generations}_generation{'' if generations == 1 else 's'}",
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

    failure_threshold = 0.8
    assert has_expected_success_rate(results, failure_threshold)


@retry(
    max_attempts=4,
    exceptions=(openai.APIConnectionError,),
    initial_delay=10,
    backoff_factor=2.0,
    logger_name="openai.api",
)
def generate_choices(generations, project_description, system_prompt) -> List[Choice]:
========
>>>>>>>> 8802138 (Add `openlit` example):examples/openlit/tests/example_1_openlit_integration/test_results_available_in_openlit.py
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
            lambda reporter, content=response: run_allocation_test(
                reporter, skills_data=skills_data, response=content
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

import json
from pathlib import Path
from typing import List

import openai
import pytest
from helpers import load_json_fixture, natural_sort_key
from jsonschema import FormatChecker, validate
from openai import OpenAI
from openai.types.chat.chat_completion import Choice
from retry import retry
from settings import root_dir

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


def test_is_within_expected():
    assert is_within_expected(0.8, 0, 5)
    assert is_within_expected(0.8, 2, 5)
    assert not is_within_expected(0.8, 3, 5)
    assert not is_within_expected(0.8, 4, 5)
    assert not is_within_expected(0.8, 5, 5)
    assert is_within_expected(0.8, 26, 100)
    assert is_within_expected(0.8, 14, 100)
    assert is_within_expected(0.97, 1, 2)
    small_size_warning = "after measuring 2x 100 runs and getting 3 failures"
    assert is_within_expected(0.97, 0, 1), small_size_warning


def is_within_expected(success_rate: float, failure_count: int, sample_size: int) -> bool:
    if sample_size <= 1:
        return True
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


def test_sort_names_with_numbers():
    unsorted = [
        "example_1_text_response",
        "example_10_threshold",
        "example_2_unit",
        "example_8_retry_network",
        "example_9_retry_with_open_telemetry",
    ]
    assert [
        "example_10_threshold",
        "example_1_text_response",
        "example_2_unit",
        "example_8_retry_network",
        "example_9_retry_with_open_telemetry",
    ] == sorted(unsorted), "The list should be sorted by the number in the name"

    correctly_sorted = [
        "example_1_text_response",
        "example_2_unit",
        "example_8_retry_network",
        "example_9_retry_with_open_telemetry",
        "example_10_threshold",
    ]
    assert sorted([Path(p) for p in unsorted], key=natural_sort_key) == [
        Path(p) for p in correctly_sorted
    ], "example_10_threshold should be last, while example_1_text_response should be first"


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


@pytest.fixture
def assert_success_rate():
    def _assert_success_rate(actual: list[bool], expected: float):
        number_of_successes = sum(1 for r in actual if r)
        actual_success_rate = number_of_successes / len(actual)
        assert actual_success_rate >= 0.0, (
            f"Cannot have less than 0% success rate, was: {actual_success_rate}"
        )
        assert actual_success_rate <= 1.0, (
            f"Cannot have more than 100% success rate, was: {actual_success_rate}"
        )
        actual_count = len(actual)
        analysis = analyse_sample_from_test(number_of_successes, actual_count)
        # Handle case when a list of results is passed
        lower_boundary = analysis.confidence_interval_prop[0]
        higher_boundary = analysis.confidence_interval_prop[1]
        assert expected > lower_boundary, f"""
            Broken Record:  
            New Success rate {analysis.proportion:.3f} with 90% confidence exceeds expected: {expected}
            Expecting: {lower_boundary:.3f} <= {expected:.3f} <= {higher_boundary:.3f}
            Got: expected={expected} <= analysis.lower_interval={lower_boundary}
            """
        assert expected < higher_boundary, f"""
            Failure rate {analysis.proportion} not within 90% confidence of expected {expected}
            New Success rate {analysis.proportion} with 90% confidence lower that expected: {expected}
            Expecting: {lower_boundary} <= {expected} <= {higher_boundary}
            Got:  analysis.higher_boundary={higher_boundary} <= expected={expected}
            """

    return _assert_success_rate


def process_row(row: tuple[int, int, float]) -> str:
    return f"{row[0]} failures out of {row[1]} is within {row[2] * 100:.0f}% success rate"


@pytest.mark.parametrize(
    "row",
    [(1, 5, 0.97), (2, 5, 0.95), (6, 100, 0.97), (15, 100, 0.80), (27, 100, 0.80)],
    ids=lambda row: process_row(row),
)
def test_success_rate_is_within_expected_error_margin_with_90_percent_confidence(
    assert_success_rate, row
):
    failure_count, total_test_runs, expected_rate = row
    results = generate_examples(failure_count, total_test_runs)
    assert_success_rate(results, expected_rate)


def generate_examples(failure_count, total_test_runs):
    return failure_count * [False] + (total_test_runs - failure_count) * [True]


@pytest.mark.parametrize(
    "row",
    [
        (
            1,
            10,
            0.70,
            [
                "New Success rate 0.900 with 90% confidence exceeds expected: 0.7",
                "Expecting: 0.74 <= 0.70 <= 1.06",
                "Got: expected=0.7 <= analysis.lower_interval=0.74",
                "assert 0.7 > 0.74",
            ],
        ),
        (
            1,
            1000,
            0.98,
            [
                "New Success rate 0.999 with 90% confidence exceeds expected: 0.98",
                "Expecting: 1.00 <= 0.98 <= 1.00",
                "Got: expected=0.98 <= analysis.lower_interval=0.997",
                "assert 0.98 > 0.997",
            ],
        ),
    ],
    ids=lambda row: row[-1][0],
)
def test_beyond_expected_success_rate(assert_success_rate, row):
    failure_count, total_test_runs, expected_rate, success_messages = row
    results = generate_examples(failure_count, total_test_runs)
    with pytest.raises(AssertionError) as excinfo:
        assert_success_rate(results, expected_rate)

    message = str(excinfo.value)
    for expected_message in success_messages:
        assert expected_message in message
    assert "Expecting: " in message
    assert "Got: expected=0" in message
    assert "<= analysis.lower_interval=0." in message
    assert "assert " in message


def test_exceeding_expected_success_rate(assert_success_rate):
    results = [True] * 1000  # example results
    results[0] = False
    expected_rate = 0.97

    try:
        assert_success_rate(results, expected_rate)
    except AssertionError as e:
        message = e.args[0]
        assert "with 90% confidence" in message
        assert "Expecting: 1.00 <= 0.97 <= 1.00" in message
        assert "Got: expected=0.97 <= analysis.lower_interval=0.99735" in message
        print(f"Assertion failed: {e}")


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

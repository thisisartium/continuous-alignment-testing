import json

from helpers import load_json_fixture
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


def has_expected_success_rate(results: list[bool], expected_success_rate: float) -> bool:
    if not results:
        return True

    failure_count = sum(not result for result in results)
    total_count = len(results)
    failure_rate = float(failure_count) / float(total_count)
    print(1.0 - failure_rate)
    return expected_success_rate <= (1.0 - failure_rate)


def test_allocations():
    tries = Runner.get_sample_size(3)
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
    test_reporter = Reporter(
        "test_allocations_threshold",
        metadata={
            "system_prompt": system_prompt,
            "user_prompt": project_description,
        },
        output_dir=ROOT_DIR,
    )
    test_runner = Runner(
        lambda reporter: run_allocation_test(reporter=reporter, skills_data=skills_data),
        reporter=test_reporter,
    )
    results = test_runner.run_multiple(tries)
    failure_threshold = 0.8
    assert has_expected_success_rate(results, failure_threshold)


def run_allocation_test(reporter, skills_data) -> bool:
    client = OpenAI()
    assert client is not None

    acceptable_people = ["Sam Thomas", "Drew Anderson", "Alex Wilson", "Alex Johnson"]
    all_developers = get_all_developer_names(skills_data)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": reporter.metadata["system_prompt"]},
            {"role": "user", "content": reporter.metadata["user_prompt"]},
        ],
        response_format={"type": "json_object"},
    )
    response = completion.choices[0].message.content
    developer_is_appropriate = any(name in response for name in acceptable_people)
    result = False
    try:
        json_object = json.loads(response)
        developer_names = get_developer_names_from_response(json_object)
        no_developer_name_is_hallucinated = False not in [
            name in all_developers for name in developer_names
        ]

        reporter.report(
            json_object,
            {
                "correct_developer_suggested": developer_is_appropriate,
                "no_developer_name_is_hallucinated": no_developer_name_is_hallucinated,
            },
        )
        result: bool = developer_is_appropriate and no_developer_name_is_hallucinated
    except json.JSONDecodeError as e:
        print(f"JSON Exception: {e}")
    return result

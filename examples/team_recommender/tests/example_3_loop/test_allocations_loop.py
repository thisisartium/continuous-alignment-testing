import json

from helpers import load_json_fixture
from openai import OpenAI
from settings import ROOT_DIR

from cat_ai.reporter import Reporter
from cat_ai.runner import Runner


def test_allocations():
    tries = 2
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
        "test_allocations_loop",
        metadata={
            "system_prompt": system_prompt,
            "user_prompt": project_description,
        },
        output_dir=ROOT_DIR,
    )
    test_runner = Runner(
        run_allocation_test,
        reporter=test_reporter,
    )
    results = test_runner.run_multiple(tries)
    assert True in results or len(results) <= 1, ("because statistically if success rate is 95% we should get at least "
                                                  "one success in a list with length greater than 1")


def run_allocation_test(reporter) -> bool:
    client = OpenAI()
    assert client is not None

    acceptable_people = ["Sam Thomas", "Drew Anderson", "Alex Wilson", "Alex Johnson"]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": reporter.metadata["system_prompt"]},
            {"role": "user", "content": reporter.metadata["user_prompt"]},
        ],
        response_format={"type": "json_object"},
    )
    response = completion.choices[0].message.content
    result = any(name in response for name in acceptable_people)
    try:
        json_object = json.loads(response)
        reporter.report(json_object, {"correct_developer_suggested": result})
    except json.JSONDecodeError as e:
        print(f"JSON Exception: {e}")
    return result

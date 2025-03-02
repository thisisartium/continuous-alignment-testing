from tests.settings import ROOT_DIR
from openai import OpenAI


def test_response_shows_developer_names():
    client = OpenAI()
    assert client is not None

    system_prompt = f"""
        You will get a description of a project, and your task is to tell me the best developers from the given list for the project
         based on their skills.
        Today's date is April 15th, 2025.
        Pick only developers who are available after the project start date. Pick people with higher skill levels first.

        Here is the skills data:
        Sam Thomas - Objective-C
        Drew Anderson - Swift, on vacation June 1st - June 10th
        Joe Smith - Android
        Robert Sanders - React Native
        """

    project_description = """
        This is a mobile iOS project for a telecom company. The project starts June 3rd.
        It will find exciting moments from sports highlights videos. The app should only work on iPhone, not iPad.
        The tech stack is iOS Native.
        """
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": project_description},
        ],
    )
    response = completion.choices[0].message.content
    print(response)
    assert "Sam Thomas" in response
    for name in ["Drew Anderson", "Joe Smith", "Robert Sanders"]:
        assert name not in response

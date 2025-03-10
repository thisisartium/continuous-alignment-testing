from openai import OpenAI


def test_response_shows_developer_names():
    client = OpenAI()
    assert client is not None

    system_prompt = """
        You will get a description of a project, and your task is to tell me the best developers from the given list for the project
         based on their skills.
        Today's date is April 15th, 2025.
        Pick only developers who are available after the project start date. Pick people with higher skill levels first.

        Here is the skills data:
        Sam Thomas - Swift, Objective-C
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
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": project_description},
        ],
    )
    response = completion.choices[0].message.content
    print(response)
    # For the iOS Native project starting on June 3rd, the best developers based on the given list would be:
    #
    # 1. Sam Thomas - Specializes in Swift and Objective-C, and is available for the project.
    # 2. Drew Anderson - Specializes in Swift but will be on vacation from June 1st to June 10th, so they are not available when the project starts.
    #
    # Therefore, Sam Thomas is the most suitable developer for this project.
    assert "Sam Thomas" in response
    assert "Drew Anderson" in response, "Surprisingly Drew Anderson is on vacation but still in the response"

def test_llm_will_hallucinate_given_no_data():
    client = OpenAI()
    assert client is not None

    system_prompt = """
        You will get a description of a project, and your task is to tell me the best developers from the given list for the project
         based on their skills.
        Today's date is April 15th, 2025.
        Pick only developers who are available after the project start date. Pick people with higher skill levels first.

        Here is the skills data:
        """

    project_description = """
        This is a mobile iOS project for a telecom company. The project starts June 3rd.
        It will find exciting moments from sports highlights videos. The app should only work on iPhone, not iPad.
        The tech stack is iOS Native.
        """
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",  # here we use a smaller model to expose the hallucination
        # model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": project_description},
        ],
    )
    response = completion.choices[0].message.content
    print(response)
    # Here is the list of developers with their skills and availability:
    #
    # 1. Sarah Johnson
    #    - Skills: iOS Native, Mobile Development
    #    - Availability: Available starting May 1st
    #
    # 2. Alex Kim
    #    - Skills: iOS Native, iPhone Development, Video Processing
    #    - Availability: Available starting June 10th
    #
    # 3. Jamie Smith
    #    - Skills: iOS Native, Mobile UI Design
    #    - Availability: Available starting May 20th
    #
    # Based on the project requirements and availability, the best developer for this mobile iOS project for the telecom company would be:
    #
    # 1. Sarah Johnson
    #     - Skills: iOS Native, Mobile Development
    #     - Availability: Available starting May 1st
    #
    # 2. Jamie Smith
    #     - Skills: iOS Native, Mobile UI Design
    #     - Availability: Available starting May 20th
    assert "Sam Thomas" not in response, "LLM obviously could not get our expected developer and will hallucinate"
    assert "Drew Anderson" not in response, "Response will contain made up names"
    assert len(response.split('\n')) > 5, "response contains list of made up developers in multiple lines"
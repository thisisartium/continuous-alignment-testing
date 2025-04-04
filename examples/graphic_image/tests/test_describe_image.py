import base64

import requests
from openai import OpenAI

from examples.graphic_image.conftest import root_path


def describe_image_by_url(image_url):
    client = OpenAI()

    user_prompt = """Describe this image in detail. 
        Do not say: image description or The image shows or The image depicts.
        IMPORTANT: Reply with the description of the image.
        """
    # Create the API request
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Or latest vision model
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    },
                ],
            }
        ],
        max_tokens=1000,
    )

    # Return the description
    return response.choices[0].message.content


def describe_image(path):
    with open(path, "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode("utf-8")
        return describe_image_by_url(f"data:image/jpeg;base64,{encoded_image}")


def test_image_was_described():
    image_url = (
        "https://cdn2.picryl.com/photo/2011/08/31/"
        "an-afghan-local-policeman-monitors-suspicious-activity-7a0054-1024.jpg"
    )
    local_path = (
        root_path
        / "tests"
        / "fixtures"
        / "an-afghan-local-policeman-monitors-suspicious-activity.jpg"
    )
    description = (
        describe_image_by_url(image_url) if check_url(image_url) else describe_image(local_path)
    )
    print("image description:", description)
    assert description is not None


def check_url(image_url) -> bool:
    # noinspection PyBroadException
    try:
        response = requests.head(image_url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

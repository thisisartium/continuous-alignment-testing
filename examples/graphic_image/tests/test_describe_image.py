import base64

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
    description = describe_image(
        root_path / "tests/fixtures/an-afghan-local-policeman-monitors-suspicious-activity.jpg"
    )
    print("image description:", description)
    assert description is not None

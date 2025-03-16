from helpers import load_json_fixture
from response_matches_json_schema import response_matches_json_schema


def test_response_matches_json_schema_inline():
    name_and_age: dict = {
        "$name_and_age": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    }

    assert response_matches_json_schema({"name": "John Doe", "age": 30}, name_and_age) is True, (
        "Both fields are present"
    )
    assert response_matches_json_schema({"name": "John Doe"}, name_and_age) is False, (
        "Missing required field 'age'"
    )


def test_response_matches_json_schema_from_files():
    example_output = load_json_fixture("example_output.json")
    schema = load_json_fixture("output_schema.json")

    assert response_matches_json_schema(example_output, schema)

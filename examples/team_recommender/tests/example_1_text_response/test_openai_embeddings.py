from example_1_text_response.openai_embeddings import (
    stabilize_embedding,
    stabilize_embedding_object,
    stabilize_float,
)


def test_stabilize_float():
    assert stabilize_float(0.0000000006) == 0.0000000005999999941330714, (
        "stabilize_float can sometimes reduce the value a little bit"
    )
    assert stabilize_float(0.000000006) == 0.000000006000000052353016, (
        "stabilize_float can sometimes increase the value a little bit"
    )


def test_stabilize_float_precise():
    precise_number = 0.123456789
    assert stabilize_float(precise_number) == 0.12345679104328156


def test_stabilize_embedding():
    embedding = [0.0000000006, 0.000000006]
    assert stabilize_embedding(embedding) == [
        0.0000000005999999941330714,
        0.000000006000000052353016,
    ]


def test_stabilize_embedding_object():
    embedding_object = {
        "text": "This is a test sentence.",
        "model": "text-embedding-3-large",
        "embedding": [0.0000000006, 0.000000006],
    }
    assert stabilize_embedding_object(embedding_object) == {
        "text": "This is a test sentence.",
        "model": "text-embedding-3-large",
        "embedding": [
            0.0000000005999999941330714,
            0.000000006000000052353016,
        ],
    }

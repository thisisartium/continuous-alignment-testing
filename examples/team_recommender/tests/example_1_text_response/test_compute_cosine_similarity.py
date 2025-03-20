import json

import pytest
from example_1_text_response.cosine_similarity import compute_alignment, compute_cosine_similarity
from example_1_text_response.openai_embeddings import create_embedding_object
from helpers import load_json_fixture


def test_compute_cosine_similarity():
    assert compute_cosine_similarity([1, 2, 3], [1, 2, 3]) == 1.0
    assert compute_cosine_similarity([-1, -2, -3], [1, 2, 3]) == -1.0

    saved_response = load_json_fixture("hallucination_response.json")
    cosine_similarity = compute_cosine_similarity(
        saved_response["embedding"], saved_response["embedding"]
    )
    assert cosine_similarity == pytest.approx(1.0)

def test_reproducing_the_same_text_embedding(snapshot):
    saved_response = load_json_fixture("hallucination_response.json")
    embedding_object = create_embedding_object(saved_response["text"], model="text-embedding-3-large")
    embedding_object_string = json.dumps(embedding_object, indent=2)
    snapshot.assert_match(embedding_object_string, "hallucination_response.json")


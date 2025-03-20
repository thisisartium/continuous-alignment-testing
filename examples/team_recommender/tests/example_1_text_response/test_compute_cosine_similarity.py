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

def test_reproducing_the_same_text_embedding():
    saved_response = load_json_fixture("hallucination_response.json")
    embedding = create_embedding_object(saved_response["text"], model="text-embedding-3-large")
    assert embedding["embedding"] == saved_response["embedding"]

def test_compute_alignment(snapshot):
    # Create embeddings using create_embedding_object
    embedding_a = create_embedding_object("This is a test sentence.", model="text-embedding-3-large")
    embedding_b = create_embedding_object("This is another test sentence.", model="text-embedding-3-large")

    # Compute the alignment vector
    alignment_vector = compute_alignment(embedding_a["embedding"], embedding_b["embedding"])

    # Convert the alignment vector to a JSON object
    alignment_json = {"alignment_vector": alignment_vector}

    # Convert the JSON object to a string
    alignment_json_string = json.dumps(alignment_json, indent=2)

    # Assert against the snapshot
    snapshot.assert_match(alignment_json_string, "alignment_vector_json_snapshot.json")
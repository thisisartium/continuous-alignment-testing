import json

import pytest
from example_1_text_response.cosine_similarity import compute_alignment
from openai_embeddings import (
    create_embedding_object,
    stabilize_embedding,
)


@pytest.mark.xfail("True", reason="Alignment vector is not stable")
def test_compute_alignment(snapshot):
    # Create embeddings using create_embedding_object
    embedding_a = create_embedding_object("This is a test sentence.")
    embedding_b = create_embedding_object("This is another test sentence.")

    # Compute the alignment vector
    alignment_vector = compute_alignment(embedding_a["embedding"], embedding_b["embedding"])
    alignment_vector = stabilize_embedding(alignment_vector)

    # Convert the alignment vector to a JSON object
    alignment_json = {"alignment_vector": alignment_vector}

    # Convert the JSON object to a string
    alignment_json_string = json.dumps(alignment_json, indent=2)

    # Assert against the snapshot
    snapshot.assert_match(alignment_json_string, "alignment_vector_json_snapshot.json")

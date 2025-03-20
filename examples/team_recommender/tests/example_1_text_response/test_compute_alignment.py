import json

from example_1_text_response.cosine_similarity import compute_alignment
from openai_embeddings import create_embedding_object


def test_compute_alignment(snapshot):
    # Create embeddings using create_embedding_object
    embedding_a = create_embedding_object(
        "This is a test sentence.", model="text-embedding-3-large"
    )
    embedding_b = create_embedding_object(
        "This is another test sentence.", model="text-embedding-3-large"
    )

    # Compute the alignment vector
    alignment_vector = compute_alignment(embedding_a["embedding"], embedding_b["embedding"])

    # Convert the alignment vector to a JSON object
    alignment_json = {"alignment_vector": alignment_vector}

    # Convert the JSON object to a string
    alignment_json_string = json.dumps(alignment_json, indent=2)

    # Assert against the snapshot
    snapshot.assert_match(alignment_json_string, "alignment_vector_json_snapshot.json")

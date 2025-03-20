import json
import os

import numpy as np
import pytest
from example_1_text_response.cosine_similarity import compute_cosine_similarity
from example_1_text_response.openai_embeddings import create_embedding_object
from helpers import load_json_fixture


def load_snapshot_value(snapshot, snapshot_filename):
    """Load a snapshot file and parse it as JSON."""
    snapshot_dir = os.path.join(
        os.path.dirname(__file__),
        'snapshots',
        "test_compute_cosine_similarity",
        "test_reproducing_the_same_text_embedding",
    )
    snapshot_path = os.path.join(snapshot_dir, snapshot_filename)

    with open(snapshot_path, "r") as f:
        return json.loads(f.read())

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
    snapshot.assert_match(embedding_object_string, "hallucination_response_large_same_text_embedding.json")



def test_embedding_equivalence(snapshot):
    snap_same = load_snapshot_value(snapshot, "hallucination_response_large_same_text_embedding.json")
    snap_different = load_snapshot_value(snapshot, "hallucination_response_large_different_text_embedding.json")
    # assert snap_same == snap_different
    diff_val = np.subtract(snap_same["embedding"], snap_different["embedding"])

    outside_tolerance_count = np.sum(np.abs(diff_val) >= 0.00001)

    # Assert a specific count (replace 0 with your expected count)
    assert outside_tolerance_count == 0, (
        f"Found {outside_tolerance_count} elements outside tolerance"
    )
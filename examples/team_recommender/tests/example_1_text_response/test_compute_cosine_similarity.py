import json
import os
from random import random

import numpy as np
import pytest
from example_1_text_response.cosine_similarity import compute_cosine_similarity
from example_1_text_response.openai_embeddings import (
    create_embedding_object,
    stabilize_embedding_object,
)
from helpers import load_json_fixture


def load_snapshot_value(snapshot, snapshot_filename):
    """Load a snapshot file and parse it as JSON."""
    snapshot_dir = os.path.join(
        os.path.dirname(__file__),
        "snapshots",
        "test_compute_cosine_similarity",
        "test_reproducing_the_same_text_embedding",
    )
    snapshot_path = os.path.join(snapshot_dir, snapshot_filename)

    with open(snapshot_path, "r") as f:
        return json.loads(f.read())


def test_compute_cosine_similarity_aligned_vectors():
    assert compute_cosine_similarity([1, 2, 3], [1, 2, 3]) == 1.0
    assert compute_cosine_similarity([-1, -2, -3], [1, 2, 3]) == -1.0


@pytest.fixture
def random_vector():
    return [random() for _ in range(100)]


def test_compute_cosine_similarity_random_vector(random_vector):
    assert compute_cosine_similarity(random_vector, random_vector) == pytest.approx(1.0)


def test_compute_cosine_similarity_opposite_vector(random_vector):
    opposite_vector = [-x for x in random_vector]
    assert compute_cosine_similarity(opposite_vector, random_vector) == pytest.approx(-1.0)


def test_compute_cosine_similarity_saved_response():
    saved_response = load_json_fixture("hallucination_response.json")
    cosine_similarity = compute_cosine_similarity(
        saved_response["embedding"], saved_response["embedding"]
    )
    assert cosine_similarity == pytest.approx(1.0)


@pytest.mark.xfail(
    reason="Snapshot fails to match and is expected to fail"
    ", but snapshot raises AssertionError in teardown"
)
def test_reproducing_the_same_text_embedding(snapshot):
    saved_response = load_json_fixture("hallucination_response.json")
    embedding_object = create_embedding_object(
        saved_response["text"], model="text-embedding-3-large"
    )
    stabilized_embedding_object = stabilize_embedding_object(embedding_object)

    embedding_object_string = json.dumps(stabilized_embedding_object, indent=2)
    with pytest.raises(AssertionError):
        snapshot.assert_match(
            embedding_object_string, "hallucination_response_large_same_text_embedding.json"
        )


def Xtest_cosine_similarity_generated_responses(snapshot):
    snap_same = load_snapshot_value(
        snapshot, "hallucination_response_large_same_text_embedding.json"
    )
    snap_different = load_snapshot_value(
        snapshot, "hallucination_response_large_different_text_embedding.json"
    )
    cosine_similarity = compute_cosine_similarity(
        snap_same["embedding"], snap_different["embedding"]
    )
    assert cosine_similarity == pytest.approx(0.99999, rel=0.00001)


def running_in_ci() -> bool:
    return os.getenv("CI") is not None


# This test is skipped on CI as it fails to produce the same diff between the two embeddings
# https://github.com/thisisartium/continuous-alignment-testing/issues/66
@pytest.mark.skipif(running_in_ci(), reason="Image comparison fails to produce diff on CI")
def Xtest_embedding_equivalence(snapshot):
    snap_same = load_snapshot_value(
        snapshot, "hallucination_response_large_same_text_embedding.json"
    )
    snap_different = load_snapshot_value(
        snapshot, "hallucination_response_large_different_text_embedding.json"
    )
    # assert snap_same == snap_different
    diff_val = np.subtract(snap_same["embedding"], snap_different["embedding"])

    outside_tolerance_count = np.sum(np.abs(diff_val) >= 0.001)

    # Assert a specific count (replace 0 with your expected count)
    assert outside_tolerance_count == 0, (
        f"Found {outside_tolerance_count} elements outside tolerance"
    )

    outside_tolerance_count = np.sum(np.abs(diff_val) >= 0.0001)

    # Assert a specific count (replace 0 with your expected count)
    assert outside_tolerance_count == 900, (
        f"Found {outside_tolerance_count} elements outside tolerance"
    )

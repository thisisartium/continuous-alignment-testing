import pytest
from example_1_text_response.cosine_similarity import compute_cosine_similarity
from helpers import load_json_fixture


def test_compute_cosine_similarity():
    assert compute_cosine_similarity([1, 2, 3], [1, 2, 3]) == 1.0
    assert compute_cosine_similarity([-1, -2, -3], [1, 2, 3]) == -1.0

    saved_response = load_json_fixture("hallucination_response.json")
    cosine_similarity = compute_cosine_similarity(
        saved_response["embedding"], saved_response["embedding"]
    )
    assert cosine_similarity == pytest.approx(1.0)

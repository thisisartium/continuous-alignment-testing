import json
import struct

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
    alignment_vector = stable_embedding(alignment_vector)

    # Convert the alignment vector to a JSON object
    alignment_json = {"alignment_vector": alignment_vector}

    # Convert the JSON object to a string
    alignment_json_string = json.dumps(alignment_json, indent=2)

    # Assert against the snapshot
    snapshot.assert_match(alignment_json_string, "alignment_vector_json_snapshot.json")


def stable_embedding(alignment_vector):
    first = alignment_vector[0]
    first_int_bits = float_to_int_same_bits(first)
    shifted = (first_int_bits << 16) >> 16
    print("first_int_bits", first_int_bits)
    print(f"shifted = {shifted}")
    return [0.0 if abs(x) < 0.0001 else massage(x) for x in alignment_vector]

def massage(x: float) -> float:
    y = (float_to_int_same_bits(x) << 16) >> 16
    return int_to_float_same_bits(y)

def test_float_to_int_same_bits():
    float_value = 3.14
    int_value = float_to_int_same_bits(float_value)
    assert int_value == 1078523331  # This is the bit representation of 3.14 in IEEE 754 format

def float_to_int_same_bits(float_value):
    # Pack the float into bytes
    packed = struct.pack("f", float_value)  # 'f' for 32-bit float

    # Unpack those same bytes as an integer
    int_value = struct.unpack("i", packed)[0]  # 'i' for 32-bit int

    return int_value

def int_to_float_same_bits(int_value):
    # Pack the integer into bytes
    packed = struct.pack("i", int_value)  # 'i' for 32-bit int

    # Unpack those same bytes as a float
    float_value = struct.unpack("f", packed)[0]  # 'f' for 32-bit float

    return float_value
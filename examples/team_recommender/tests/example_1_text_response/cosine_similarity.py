import numpy as np


def compute_cosine_similarity(a: list, b: list) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def compute_alignment(a: list, b: list) -> list:
    # Calculate the difference vector
    difference_vector = np.subtract(b, a)
    # Calculate the norm of the difference vector
    norm = np.linalg.norm(difference_vector)
    # Normalize the difference vector
    if norm == 0:
        return difference_vector  # Return the zero vector if the norm is zero
    return difference_vector / norm

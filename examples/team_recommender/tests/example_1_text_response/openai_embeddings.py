import argparse
import json
import os
import struct

from openai import OpenAI

embedding_dimensions = 256


def get_embedding(text, model: str):
    """
    Get embeddings from OpenAI API

    Args:
        text (str): Text to embed
        model (str): Model to use for embedding

    Returns:
        list: Vector embedding of the text
    """
    # Initialize the client with API key from environment
    client = OpenAI()

    # Get the embedding from OpenAI
    response = client.embeddings.create(input=text, model=model, dimensions=embedding_dimensions)

    # Extract and return the embedding vector
    return response.data[0].embedding


def stabilize_embedding(embedding):
    return list(map(stabilize_float, embedding))


def stabilize_embedding_object(embedding_object):
    return {**embedding_object, "embedding": stabilize_embedding(embedding_object["embedding"])}


def stabilize_float(x: float) -> float:
    return float(struct.unpack("f", struct.pack("f", x))[0])


def create_embedding_object(text: str) -> dict:
    return create_embedding_object_model(text, "text-embedding-3-small")


def create_embedding_object_model(text: str, model: str) -> dict:
    """
    Create an embedding object with metadata

    Args:
        text (str): Text to embed
        model (str): Model to use for embedding

    Returns:
        dict: Object with text, model and embedding
    """

    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not provided or set in environment")

    # Get the embedding
    embedding = get_embedding(text, model=model)

    # Create and return JSON object with metadata
    return {"text": text, "model": model, "embedding": embedding}


def save_embedding(embedding_obj, output_file="embedding.json"):
    """
    Save embedding object to JSON file

    Args:
        embedding_obj (dict): Embedding object with metadata
        output_file (str): Output JSON file path
    """
    with open(output_file, "w") as f:
        json.dump(embedding_obj, f, indent=2)
    return output_file


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate OpenAI embeddings and save to JSON")
    parser.add_argument("text", type=str, help="Text to embed")
    parser.add_argument("--output", type=str, default="embedding.json", help="Output JSON file")
    args = parser.parse_args()

    # Create embedding object
    embedding_obj = create_embedding_object(args.text)

    # Save to JSON file
    output_path = save_embedding(embedding_obj, args.output)
    print(f"Embedding saved to {output_path}")


if __name__ == "__main__":
    main()

import argparse
import json
import os
import struct

from openai import OpenAI


def get_embedding(text, model="text-embedding-3-small"):
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
    response = client.embeddings.create(input=text, model=model)

    # Extract and return the embedding vector
    return response.data[0].embedding


def stabilize_embedding_object(embedding_object):
    embedding_object["embedding"] = [stabilize_float(x) for x in embedding_object["embedding"]]
    return embedding_object


def stabilize_float(x: float) -> float:
    y = (float_to_int_same_bits(x) << 32) >> 32
    return int_to_float_same_bits(y)


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


def create_embedding_object(text, model="text-embedding-3-small"):
    """
    Create an embedding object with metadata

    Args:
        text (str): Text to embed
        model (str): Model to use for embedding
        api_key (str, optional): OpenAI API key

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
    parser.add_argument(
        "--model", type=str, default="text-embedding-3-small", help="OpenAI embedding model to use"
    )
    parser.add_argument("--api-key", type=str, help="OpenAI API key (optional)")
    args = parser.parse_args()

    # Create embedding object
    embedding_obj = create_embedding_object(args.text, model=args.model, api_key=args.api_key)

    # Save to JSON file
    output_path = save_embedding(embedding_obj, args.output)
    print(f"Embedding saved to {output_path}")


if __name__ == "__main__":
    main()

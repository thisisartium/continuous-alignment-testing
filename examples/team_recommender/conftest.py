import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

root_path = (Path(__file__)).parent
subfolders = ["src", "tests"]
for subfolder in subfolders:
    directory = str((root_path / subfolder).resolve())
    print(f"appending folder: {subfolder}, as directory: {directory}")
    sys.path.append(directory)

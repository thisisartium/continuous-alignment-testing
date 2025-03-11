from dotenv import load_dotenv
import sys
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

source_folder = str((Path(__file__).parent / "src").resolve())
print("source_folder", source_folder)
sys.path.append(source_folder)

# Local Setup
- install [uv](https://docs.astral.sh/uv/getting-started/installation) - Python package manager
- install dependencies
```
uv sync
```
- setup environment
```
cp .env.example .env
```
- populate your new `.env` file with required values

# Running the AI tests
- run from this directory:
```
uv run pytest
```

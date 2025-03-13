# Local Setup

### Install Package Manager

- install [uv](https://docs.astral.sh/uv/getting-started/installation) - Python package manager
  - `brew install uv`

### install dependencies

```shell
uv sync
```

### Setup environment

```shell
cp .env.example .env
```

- populate your new `.env` file with required values

### Running the AI tests

This is live documentation of a growing number of examples.  
We have a challenge when adding new examples where we have to update previous
examples to follow refactoring updates we made.

So instead, just run the latest example from the repository:

```shell
find tests -maxdepth 1 -name "example_*" -type d | sort -V | tail -n 1
```

```shell
uv run pytest $(find tests -maxdepth 1 -name "example_*" -type d | sort -V | tail -n 1)
```

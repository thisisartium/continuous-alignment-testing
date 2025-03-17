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
uv run pytest
```

by default, it will run only the tests in the latest examples directory.

For example, the output will look like this when 9 is the latest example:
```shell
tests/example_8_retry_network/test_retry_response_generation.py::test_response_pass_all_validations_and_retried SKIPPED (Only running latest example (use --all to run all))
t
tests/example_9_threshold/test_measurement_is_within_threshold.py::test_metrics_within_range {
    "test_name": "test_metrics_1_generation",
```
and example 8 got skipped.

### Running all examples AI tests

```shell
uv run pytest --all
```


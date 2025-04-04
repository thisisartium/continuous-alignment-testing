# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Install dependencies: `uv sync`
- Run tests: `uv run pytest`
- Run specific test: `uv run pytest tests/path/to/test_file.py::test_name -v`
- Run all example tests: `uv run pytest --all`
- Type check: `uv run mypy src tests examples/team_recommender/src`
- Lint: `uv run ruff check src tests examples`
- Format: `uv run ruff format src tests examples`

## Code Style
- Python 3.13+ required
- Use type annotations for all functions and methods (checked by mypy)
- Max line length: 120 characters
- Use pytest fixtures in `conftest.py` for test setup
- Follow black formatting conventions
- Import order: stdlib, third-party, local
- Use proper error handling with try/except blocks
- Use snake_case for functions, variables, and modules
- Use PascalCase for class names
- Maintain test coverage for all new code
- Use `CAT_AI_SAMPLE_SIZE` environment variable for test iterations
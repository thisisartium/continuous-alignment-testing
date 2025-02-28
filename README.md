# Continuous Alignment Testing (CAT) Framework

A framework for implementing Continuous Alignment Testing (CAT) for LLM-based applications.

## Overview

CAT provides the infrastructure needed to:

- Run and track CATs against LLM outputs
- Store and analyze test results over time
- Monitor changes in LLM behavior as prompts/models/data evolve
- Integrate validation into CI/CD pipelines

## Example Apps

- [team_recommender - Team Recommender](examples/team_recommender/readme.md)


## Run Tests

```bash
uv run pytest
```

## Code Quality

```bash
uv run mypy -p src
```

## [Publishing Documentation](https://thisisartium.github.io/continuous-alignment-testing)

The Sphinx based documentation is available at [https://thisisartium.github.io/cat-ai](https://thisisartium.github.io/cat-ai)

## [Wiki](wiki)

[wiki](https://github.com/thisisartium/continuous-alignment-testing/wiki)

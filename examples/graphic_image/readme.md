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

```shell
uv run pytest
```

# Description

This AI has to produce text descriptions when an image is submitted. All images
used are available under Creative Commons licenses, with source URL information provided below

OpenAI license keys will be required to run these examples.

### Licenses

https://picryl.com/media/an-afghan-local-policeman-monitors-suspicious-activity-7a0054

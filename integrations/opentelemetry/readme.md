# Local Setup

### Deploy openlit
#### Clone repo if necessary
```shell
git clone git@github.com:openlit/openlit.git
```
#### Start Docker Compose
Changing of the default port (`3000`) _might_ be necessary
```shell
docker compose up -d
```

### Install Package Manager

- install [uv](https://docs.astral.sh/uv/getting-started/installation) - Python package manager
  - `brew install uv`

### install dependencies

```shell
uv pip install openlit
uv sync
```

### Setup environment

```shell
cp .env.example .env
```

- populate your new `.env` file with required values

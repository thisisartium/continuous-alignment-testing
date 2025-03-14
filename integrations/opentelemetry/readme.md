# Purpose
> To provide an example of validating LLM responses through observability. This example does **not** actually use _any_ of the CAT python library functionality. It's more of an example of how one _might_ do continuous alignment through observability. Perhaps we could call that CAO, Continuous Alignment in Observability.
# Overview
> This example uses [OpenLIT](https://github.com/openlit/openlit) to auto instrument calls to an LLMs api, providing **[OpenTelemetry](https://opentelemetry.io)-native** observability. [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector-contrib) is used to process the traces and attach validations on the fly to the traces, ready for downstream visualization.

> This is a simple, hardcoded example to prove out the possiblity. There is a number of places for automation and further development that _might_ be quite time consuming.
# Running the example
## Setup (if needed)
> Clone this repo locally
```shell
git clone https://github.com/thisisartium/continuous-alignment-testing
```
> Install dependencies
#### Install package manager
* install [uv](https://docs.astral.sh/uv/getting-started/installation) - Python package manager
  * `brew install uv`
#### Install dependencies
```shell
uv pip install openlit
uv sync
```
#### Setup environment
> populate your new `.env` file with required values
```shell
cp .env.example .env
```

> Setup environment
## Running OpenTelemetry Collector
> Run the following command
```shell
docker run -p 4317:4317 -p 4318:4318 -v $(pwd)/integrations/opentelemetry/src/config.yaml:/etc/otelcol/config.yaml otel/opentelemetry-collector-contrib:latest --config /etc/otelcol/config.yaml
```
## Executing LLM calls using a test
> Run one of the tests found in `/integrations/opentelemetry/tests/test_responses_available_in_opentelemetry.py
## See the results
> Look at the logs from the OpenTelemetry Collector. At the end you'll see a line similar to the following.
```shell
validations: Map({"correct_developer_suggested":true,"no_developer_name_is_hallucinated":true,"not_empty_response":true})
```

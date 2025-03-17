#!/usr/bin/env bash

# Purpose: Determine and validate the number of runs for CI testing
# Usage: ./set-number-of-runs.sh
# Environment Variables:
#   DEFAULT_RUNS:             The default number of runs to use
#   GITHUB_REF_NAME:          The name of the branch or tag
#   INPUTS_ROUNDS_OR_EMPTY:   The number of rounds to run the tests
#   GITHUB_OUTPUT:            The path to the file to store the step output
#   GITHUB_ENV:               The path to the file to store the environment variables
#
# This script sets CAT_AI_SAMPLE_SIZE for the statistical test
# based on input or the branch name
# and stores the value in the output and environment files


[[ "${GITHUB_REF_NAME}" =~ ^ci-experiment/ ]] && ROUNDS=1 || ROUNDS=${DEFAULT_RUNS:-10}
ROUNDS=${INPUTS_ROUNDS_OR_EMPTY:-$ROUNDS}

# Validate that ROUNDS is a valid integer
if ! [[ "$ROUNDS" =~ ^[0-9]+$ ]]; then
  echo "::error title=Invalid input:: ROUNDS=$ROUNDS is not a valid integer"
  exit 1
fi

if [ "$ROUNDS" -gt 128 ] || [ "$ROUNDS" -le 0 ]
then
  echo "::error title=Invalid number of rounds:: ROUNDS=$ROUNDS, must be between 1 and 128"
  exit 1
fi

PLURAL=$([ "$ROUNDS" -eq 1 ] || echo "s")
ROUND_RUNS="${ROUNDS} run${PLURAL}"
echo "::notice::Starting ${ROUND_RUNS}"


if [ -n "$GITHUB_OUTPUT" ]
then
  echo "number_of_runs=$ROUNDS" >> "$GITHUB_OUTPUT"
fi

if [ -n "$GITHUB_ENV" ]
then
  echo "CAT_AI_SAMPLE_SIZE=$ROUNDS" >> "$GITHUB_ENV"
fi

#!/bin/bash

# Purpose: Determine and validate the number of runs for CI testing
# Usage: ./set-runs.sh [custom_rounds]

# Check if we're on a CI experiment branch
if [[ "${GITHUB_REF_NAME}" =~ ^ci-experiment/ ]]; then
  DEFAULT_ROUNDS=1
else
  DEFAULT_ROUNDS=10
fi

# Use explicitly provided input if available, otherwise use default
ROUNDS=${1:-${INPUTS_ROUNDS_OR_EMPTY:-$DEFAULT_ROUNDS}}
          
# Validate that ROUNDS is a valid integer
if ! [[ "$ROUNDS" =~ ^[0-9]+$ ]]; then
  echo "::error title=Invalid input:: ROUNDS=$ROUNDS is not a valid integer"
  exit 1
fi

# Validate range
if [ "$ROUNDS" -gt 128 ] || [ "$ROUNDS" -le 0 ]; then
  echo "::error title=Invalid number of rounds:: ROUNDS=$ROUNDS, must be between 1 and 128"
  exit 1
fi

# Provide user feedback
PLURAL_TEXT=$([ "$ROUNDS" -eq 1 ] || echo "s")
echo "::notice::Starting ${ROUNDS} run${PLURAL_TEXT}"

# Output for GitHub Actions to consume
echo "number_of_runs=$ROUNDS"
echo "CAT_AI_SAMPLE_SIZE=$ROUNDS"

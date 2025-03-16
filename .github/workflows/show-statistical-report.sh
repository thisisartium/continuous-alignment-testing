#!/usr/bin/env bash

show_usage() {
  cat << EOF
Usage: $(basename "$0") TEST_RESULTS_FOLDER

Arguments:
  TEST_RESULTS_FOLDER  Path to the folder containing test result files.

Environment Variables:
  GITHUB_STEP_SUMMARY  Path to the file where the step summary is stored.
  CAT_AI_SAMPLE_SIZE   Number of samples to use for the statistical test.

Description:
  This script generates a statistical report of the project's test results
  by counting the number of passed and failed tests within the specified folder.

  Failures: fail-*.json
  Passing: pass-*.json

EOF
}

# Check if no arguments are provided or if help is requested
if [ $# -eq 0 ] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
  show_usage
  exit 1
fi

TEST_RESULTS_FOLDER=$1

# Validate the provided directory
if [ ! -d "$TEST_RESULTS_FOLDER" ]; then
  echo "::error:: The test results folder does not exist: $TEST_RESULTS_FOLDER"
  exit 2
fi

# This script is used to show the statistical report of the project.
FAILURE_COUNT=$(find "$TEST_RESULTS_FOLDER" -type f -name "fail-*.json" | wc -l)
PASS_COUNT=$(find "$TEST_RESULTS_FOLDER" -type f -name "pass-*.json" | wc -l)
TOTAL_COUNT=$((FAILURE_COUNT + PASS_COUNT))

if [ "$TOTAL_COUNT" -eq 0 ]
then
  echo "::error file:show-statistical-report.sh,line=$LINENO,title=Total Count is Zero:: TOTAL_COUNT of test results is zero. FAILURE_COUNT=$FAILURE_COUNT, PASS_COUNT=$PASS_COUNT"
  exit 0
fi

if [ -n "$CAT_AI_SAMPLE_SIZE" ] && [ $TOTAL_COUNT -ne $CAT_AI_SAMPLE_SIZE ]
then
  echo "::error file:show-statistical-report.sh,line=$LINENO,title=Not all tests succeeded:: CAT_AI_SAMPLE_SIZE != TOTAL_COUNT: CAT_AI_SAMPLE_SIZE=$CAT_AI_SAMPLE_SIZE, TOTAL_COUNT=$TOTAL_COUNT"
fi

PYTHONPATH=src uv run python -m cat_ai.reporter \
  "$FAILURE_COUNT" \
  "$TOTAL_COUNT" \
  >> "$GITHUB_STEP_SUMMARY"

echo ::notice title=Statistical Outcome::Successes: $PASS_COUNT, Failures: $FAILURE_COUNT from total: $TOTAL_COUNT, sample size: $CAT_AI_SAMPLE_SIZE

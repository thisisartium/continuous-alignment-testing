#!/usr/bin/env bash

show_usage() {
  cat << EOF
Usage: $(basename "$0") TEST_RESULTS_FOLDER

Arguments:
  TEST_RESULTS_FOLDER  Path to the folder containing test result files.

Description:
  This script generates a statistical report of the project's test results by counting the number of passed and failed tests within the specified folder.

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
  echo "::error:: TOTAL_COUNT of test results is zero. FAILURE_COUNT=$FAILURE_COUNT, PASS_COUNT=$PASS_COUNT"
  exit 0
fi

PYTHONPATH=src uv run python -m cat_ai.reporter \
  "$FAILURE_COUNT" \
  "$TOTAL_COUNT" \
  >> "$GITHUB_STEP_SUMMARY"

cat <<________Github_Job_Summary_Notice
::notice:: CAT AI Statistical Report
Failures: $FAILURE_COUNT from sample size: $TOTAL_COUNT
Successes: $PASS_COUNT from sample size: $TOTAL_COUNT
________Github_Job_Summary_Notice
#!/bin/bash

# Input variables
FAILURE_COUNT=$1
SAMPLE_SIZE=$2
CONFIDENCE_LEVEL=0.95

# Calculate sample proportion
p_hat=$(echo "scale=4; $FAILURE_COUNT / $SAMPLE_SIZE" | bc)

# Determine z-score for the given confidence level
# For 95% confidence level, z-score is approximately 1.96
z=1.96

# Calculate standard error
SE=$(echo "scale=6; sqrt($p_hat * (1 - $p_hat) / $SAMPLE_SIZE)" | bc)

# Calculate margin of error
ME=$(echo "scale=6; $z * $SE" | bc)

# Calculate confidence interval bounds as proportions
LOWER_BOUND_PROP=$(echo "scale=6; $p_hat - $ME" | bc)
UPPER_BOUND_PROP=$(echo "scale=6; $p_hat + $ME" | bc)

# Convert proportion bounds to integer counts
LOWER_BOUND_COUNT=$(echo "$LOWER_BOUND_PROP * $SAMPLE_SIZE" | bc | awk '{print ($1 > int($1)) ? int($1) + 1 : int($1)}')
UPPER_BOUND_COUNT=$(echo "$UPPER_BOUND_PROP * $SAMPLE_SIZE / 1"  | bc)

echo "> [!NOTE] There are $FAILURE_COUNT failures out of $SAMPLE_SIZE generations.
> Sample Proportion (p̂): $p_hat
> Standard Error (SE): $SE
> Margin of Error (ME): $ME
> 95% Confidence Interval: [$LOWER_BOUND_PROP, $UPPER_BOUND_PROP]
> 95% Confidence Interval (Count): [$LOWER_BOUND_COUNT, $UPPER_BOUND_COUNT]"
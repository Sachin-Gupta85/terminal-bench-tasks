#!/usr/bin/env bash
# Reference (oracle) solution for log-error-summary.
# Counts exact-match ERROR lines per service and writes ordered JSON.
set -euo pipefail

cat /app/logs/*.log \
  | awk '$2 == "ERROR" { count[$3]++ } END { for (s in count) print count[s], s }' \
  | sort -k1,1nr -k2,2 \
  | jq -R -s 'split("\n")
      | map(select(length > 0) | split(" ") | {(.[1]): (.[0] | tonumber)})
      | add // {}' \
  > /app/error_summary.json

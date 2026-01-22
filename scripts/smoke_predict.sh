#!/usr/bin/env bash
set -euo pipefail

: "${ENDPOINT_ID:?set ENDPOINT_ID}"
: "${REGION:=europe-west2}"

cat > /tmp/request.json <<JSON
{"instances":[[1,10],[2,20],[5,50]]}
JSON

gcloud ai endpoints predict "$ENDPOINT_ID" \
  --region="$REGION" \
  --json-request=/tmp/request.json

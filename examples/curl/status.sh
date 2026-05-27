#!/usr/bin/env bash
# Query XingShu BCI local API status.
# Usage:
#   export XINGSHU_BCI_TOKEN=xs_live_xxxx
#   export XINGSHU_BCI_BASE_URL=http://127.0.0.1:54321
#   ./status.sh

set -euo pipefail

if [[ -z "${XINGSHU_BCI_TOKEN:-}" ]]; then
  echo "XINGSHU_BCI_TOKEN env var is required." >&2
  exit 1
fi

BASE="${XINGSHU_BCI_BASE_URL:-http://127.0.0.1:0}"
curl -fsS -H "Authorization: Bearer ${XINGSHU_BCI_TOKEN}" "${BASE}/v1/status" | jq .

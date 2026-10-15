#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 EPISODE_NUMBER" >&2
  exit 2
fi
movi render "$1"

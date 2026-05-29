#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENERATOR_PY="${SCRIPT_DIR}/generate_codebase_context.py"
PYTHON_CMD=""

if [[ ! -f "${GENERATOR_PY}" ]]; then
  echo "Generator script not found: ${GENERATOR_PY}" >&2
  exit 1
fi

select_python() {
  local candidate
  for candidate in python3 python; do
    if ! command -v "${candidate}" >/dev/null 2>&1; then
      continue
    fi
    if "${candidate}" - >/dev/null 2>&1 <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 10) else 1)
PY
    then
      PYTHON_CMD="${candidate}"
      return 0
    fi
  done
  return 1
}

if ! select_python; then
  echo "python 3.10 or newer interpreter not found" >&2
  exit 1
fi

"${PYTHON_CMD}" "${GENERATOR_PY}" "$@"
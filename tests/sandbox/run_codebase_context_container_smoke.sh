#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DOCKERFILE="${SCRIPT_DIR}/base/Dockerfile"
IMAGE_TAG="${IMAGE_TAG:-agent-skills-lab/codebase-context-sandbox:local}"

PYTEST_ARGS=("$@")
if [[ ${#PYTEST_ARGS[@]} -eq 0 ]]; then
  PYTEST_ARGS=(
    "tests/integration/test_codebase_context_installed_smoke.py"
    "-q"
  )
fi

if [[ "${SKIP_BUILD:-0}" != "1" ]]; then
  docker build \
    --tag "${IMAGE_TAG}" \
    --file "${DOCKERFILE}" \
    "${REPO_ROOT}"
fi

docker run \
  --rm \
  --volume "${REPO_ROOT}:/workspace" \
  --workdir /workspace \
  "${IMAGE_TAG}" \
  python -m pytest "${PYTEST_ARGS[@]}"

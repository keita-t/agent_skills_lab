#!/usr/bin/env bash
set -euo pipefail

SCRIPT_SOURCE="${BASH_SOURCE[0]}"
if [[ "${SCRIPT_SOURCE}" != */* ]]; then
  SCRIPT_SOURCE="./${SCRIPT_SOURCE}"
fi
SCRIPT_DIR="$(cd -- "${SCRIPT_SOURCE%/*}" && pwd -P)"
RUNTIME_DOCKERFILE="${SCRIPT_DIR}/Dockerfile"
RUNTIME_HELPER="${SCRIPT_DIR}/../runtime_container_lib.sh"
RUNTIME_IMAGE="${CODEBASE_CONTEXT_RUNTIME_IMAGE:-agent-skills-lab/codebase-context-runtime:local}"
DEFAULT_OUTPUT_NAME="CODEBASE_CONTEXT.md"

if [[ ! -f "${RUNTIME_DOCKERFILE}" ]]; then
  echo "Runtime Dockerfile not found: ${RUNTIME_DOCKERFILE}" >&2
  exit 1
fi

if [[ ! -f "${RUNTIME_HELPER}" ]]; then
  echo "Runtime helper not found: ${RUNTIME_HELPER}" >&2
  exit 1
fi

# shellcheck source=../runtime_container_lib.sh
source "${RUNTIME_HELPER}"

if ! runtime_container_require_docker; then
  echo "docker is required for codebase-context runtime" >&2
  exit 1
fi

runtime_container_collect_common_args "--repo-root" "--output" "$@"

CURRENT_WORKDIR="$(pwd -P)"
REPO_ROOT="${RUNTIME_CONTAINER_EXPLICIT_REPO_ROOT}"
if [[ -z "${REPO_ROOT}" ]]; then
  REPO_ROOT="$(runtime_container_discover_repo_root "${CURRENT_WORKDIR}")"
fi

CONTAINER_WORKDIR="$(runtime_container_compute_workdir "${CURRENT_WORKDIR}" "${REPO_ROOT}")"

runtime_container_build_image "${RUNTIME_IMAGE}" "${RUNTIME_DOCKERFILE}" "${SCRIPT_DIR}"
runtime_container_run "${RUNTIME_IMAGE}" "${REPO_ROOT}" "${CONTAINER_WORKDIR}" "${DEFAULT_OUTPUT_NAME}"

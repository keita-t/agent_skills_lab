#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DOCKERFILE="${SCRIPT_DIR}/base/Dockerfile"
IMAGE_TAG="${IMAGE_TAG:-agent-skills-lab/codebase-context-sandbox:local}"
mkdir -p "${REPO_ROOT}/.tmp"
SANDBOX_ROOT="$(mktemp -d "${REPO_ROOT}/.tmp/codebase-context-smoke.XXXXXX")"
TARGET_ROOT="${SANDBOX_ROOT}/target-repo"
LAUNCHER="${TARGET_ROOT}/.github/ecosystems/codebase-context/generate_codebase_context.sh"
SANDBOX_NAME="$(basename "${SANDBOX_ROOT}")"
PREP_SCRIPT="${SANDBOX_ROOT}/prepare_target.py"
CONTAINER_ID=""

cleanup() {
  if [[ -n "${CONTAINER_ID}" ]]; then
    docker rm -f "${CONTAINER_ID}" >/dev/null 2>&1 || true
  fi
  rm -rf "${SANDBOX_ROOT}"
}

trap cleanup EXIT

if [[ "${SKIP_BUILD:-0}" != "1" ]]; then
  docker build \
    --tag "${IMAGE_TAG}" \
    --file "${DOCKERFILE}" \
    "${REPO_ROOT}"
fi

cat > "${PREP_SCRIPT}" <<PY
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, "/workspace/.github/ecosystems")

from ecosystem_delivery_service import apply_delivery_changes, build_install_changeset

target_root = Path("/workspace/.tmp/${SANDBOX_NAME}/target-repo")
target_root.mkdir(parents=True, exist_ok=True)
subprocess.run(["git", "init", "-q", str(target_root)], check=True)
(target_root / "src" / "internal").mkdir(parents=True, exist_ok=True)
(target_root / "src" / "main.py").write_text("print('main')\\n", encoding="utf-8")
(target_root / "src" / "internal" / "skip.py").write_text(
  "print('skip')\\n",
  encoding="utf-8",
)
(target_root / "README.md").write_text("# Sandbox\\n", encoding="utf-8")

apply_delivery_changes(
  build_install_changeset(
    target_root=target_root,
    ecosystem_slug="codebase-context",
  )
)
PY

CONTAINER_ID="$(docker create --workdir /workspace "${IMAGE_TAG}" python /tmp/prepare_target.py)"
docker cp "${REPO_ROOT}/." "${CONTAINER_ID}:/workspace"
docker cp "${PREP_SCRIPT}" "${CONTAINER_ID}:/tmp/prepare_target.py"
docker start -a "${CONTAINER_ID}"
docker cp "${CONTAINER_ID}:/workspace/.tmp/${SANDBOX_NAME}/target-repo" "${SANDBOX_ROOT}"
docker rm -f "${CONTAINER_ID}" >/dev/null 2>&1 || true
CONTAINER_ID=""

if [[ ! -x "${LAUNCHER}" ]]; then
  echo "Installed runtime launcher not found: ${LAUNCHER}" >&2
  exit 1
fi

"${LAUNCHER}" \
  --repo-root "${TARGET_ROOT}" \
  --include "src/**" \
  --exclude "src/internal/**" \
  --output "narrow.md"

grep -q "### src/main.py" "${TARGET_ROOT}/narrow.md"
if grep -q "### src/internal/skip.py" "${TARGET_ROOT}/narrow.md"; then
  echo "Excluded file leaked into narrow.md" >&2
  exit 1
fi
if grep -q "### README.md" "${TARGET_ROOT}/narrow.md"; then
  echo "README.md should not appear in narrow.md" >&2
  exit 1
fi

if "${LAUNCHER}" \
  --repo-root "${TARGET_ROOT}" \
  --include "missing/**" \
  --output "empty.md" \
  >"${SANDBOX_ROOT}/empty.stdout" 2>"${SANDBOX_ROOT}/empty.stderr"; then
  echo "Expected empty-scope export to fail" >&2
  exit 1
fi

grep -q "No repository files matched the selected export scope" "${SANDBOX_ROOT}/empty.stderr"
if [[ -e "${TARGET_ROOT}/empty.md" ]]; then
  echo "empty.md should not be created after an empty-scope failure" >&2
  exit 1
fi

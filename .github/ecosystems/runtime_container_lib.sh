#!/usr/bin/env bash

RUNTIME_CONTAINER_ARGS=()
RUNTIME_CONTAINER_EXPLICIT_REPO_ROOT=""
RUNTIME_CONTAINER_OUTPUT_ARGUMENT=""
RUNTIME_CONTAINER_OUTPUT_ARGUMENT_IS_ABSOLUTE=0
RUNTIME_CONTAINER_OUTPUT_WAS_EXPLICIT=0
RUNTIME_CONTAINER_REPO_ROOT_FLAG=""
RUNTIME_CONTAINER_OUTPUT_FLAG=""

runtime_container_require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "docker is required for installed container runtimes" >&2
    return 1
  fi
}

runtime_container_resolve_directory() {
  local candidate="$1"
  if [[ ! -d "${candidate}" ]]; then
    echo "Directory not found: ${candidate}" >&2
    return 1
  fi
  (
    cd -- "${candidate}"
    pwd -P
  )
}

runtime_container_discover_repo_root() {
  local candidate="$1"

  while true; do
    if [[ -e "${candidate}/.git" || -d "${candidate}/.github" ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
    if [[ "${candidate}" == "/" ]]; then
      echo "Could not locate the repository root. Pass --repo-root." >&2
      return 1
    fi

    candidate="${candidate%/*}"
    if [[ -z "${candidate}" ]]; then
      candidate="/"
    fi
  done
}

runtime_container_reset_common_state() {
  RUNTIME_CONTAINER_ARGS=()
  RUNTIME_CONTAINER_EXPLICIT_REPO_ROOT=""
  RUNTIME_CONTAINER_OUTPUT_ARGUMENT=""
  RUNTIME_CONTAINER_OUTPUT_ARGUMENT_IS_ABSOLUTE=0
  RUNTIME_CONTAINER_OUTPUT_WAS_EXPLICIT=0
  RUNTIME_CONTAINER_REPO_ROOT_FLAG=""
  RUNTIME_CONTAINER_OUTPUT_FLAG=""
}

runtime_container_collect_common_args() {
  local repo_root_flag="$1"
  local output_flag="$2"
  shift 2

  runtime_container_reset_common_state
  RUNTIME_CONTAINER_REPO_ROOT_FLAG="${repo_root_flag}"
  RUNTIME_CONTAINER_OUTPUT_FLAG="${output_flag}"

  local args=("$@")
  local index=0

  while [[ ${index} -lt ${#args[@]} ]]; do
    local arg="${args[${index}]}"

    if [[ -n "${repo_root_flag}" && "${arg}" == "${repo_root_flag}" ]]; then
      if [[ $((index + 1)) -ge ${#args[@]} ]]; then
        echo "${repo_root_flag} requires a directory path" >&2
        return 1
      fi
      RUNTIME_CONTAINER_EXPLICIT_REPO_ROOT="$(runtime_container_resolve_directory "${args[$((index + 1))]}")" || return 1
      RUNTIME_CONTAINER_ARGS+=("${repo_root_flag}" "${RUNTIME_CONTAINER_EXPLICIT_REPO_ROOT}")
      index=$((index + 2))
      continue
    fi

    if [[ -n "${repo_root_flag}" && "${arg}" == ${repo_root_flag}=* ]]; then
      RUNTIME_CONTAINER_EXPLICIT_REPO_ROOT="$(runtime_container_resolve_directory "${arg#${repo_root_flag}=}")" || return 1
      RUNTIME_CONTAINER_ARGS+=("${repo_root_flag}=${RUNTIME_CONTAINER_EXPLICIT_REPO_ROOT}")
      index=$((index + 1))
      continue
    fi

    if [[ -n "${output_flag}" && "${arg}" == "${output_flag}" ]]; then
      if [[ $((index + 1)) -ge ${#args[@]} ]]; then
        echo "${output_flag} requires a path" >&2
        return 1
      fi
      RUNTIME_CONTAINER_OUTPUT_ARGUMENT="${args[$((index + 1))]}"
      RUNTIME_CONTAINER_OUTPUT_WAS_EXPLICIT=1
      if [[ "${RUNTIME_CONTAINER_OUTPUT_ARGUMENT}" == /* ]]; then
        RUNTIME_CONTAINER_OUTPUT_ARGUMENT_IS_ABSOLUTE=1
      fi
      RUNTIME_CONTAINER_ARGS+=("${output_flag}" "${RUNTIME_CONTAINER_OUTPUT_ARGUMENT}")
      index=$((index + 2))
      continue
    fi

    if [[ -n "${output_flag}" && "${arg}" == ${output_flag}=* ]]; then
      RUNTIME_CONTAINER_OUTPUT_ARGUMENT="${arg#${output_flag}=}"
      RUNTIME_CONTAINER_OUTPUT_WAS_EXPLICIT=1
      if [[ "${RUNTIME_CONTAINER_OUTPUT_ARGUMENT}" == /* ]]; then
        RUNTIME_CONTAINER_OUTPUT_ARGUMENT_IS_ABSOLUTE=1
      fi
      RUNTIME_CONTAINER_ARGS+=("${arg}")
      index=$((index + 1))
      continue
    fi

    RUNTIME_CONTAINER_ARGS+=("${arg}")
    index=$((index + 1))
  done
}

runtime_container_compute_workdir() {
  local current_workdir="$1"
  local repo_root="$2"

  if [[ "${current_workdir}" == "${repo_root}" || "${current_workdir}" == "${repo_root}"/* ]]; then
    printf '%s\n' "${current_workdir}"
    return 0
  fi

  printf '%s\n' "${repo_root}"
}

runtime_container_build_image() {
  local runtime_image="$1"
  local runtime_dockerfile="$2"
  local build_context="$3"

  docker build \
    --tag "${runtime_image}" \
    --file "${runtime_dockerfile}" \
    "${build_context}"
}

runtime_container_bind_mount_probe() {
  local runtime_image="$1"
  local repo_root="$2"

  docker run \
    --rm \
    --entrypoint sh \
    --volume "${repo_root}:${repo_root}" \
    "${runtime_image}" \
    -c 'test -d "$1" && { test -d "$1/.git" || test -d "$1/.github"; }' \
    sh \
    "${repo_root}" \
    >/dev/null 2>&1
}

runtime_container_run_with_bind_mounts() {
  local runtime_image="$1"
  local repo_root="$2"
  local container_workdir="$3"

  docker run \
    --rm \
    --user "${UID}" \
    --volume "${repo_root}:${repo_root}" \
    --workdir "${container_workdir}" \
    "${runtime_image}" \
    "${RUNTIME_CONTAINER_ARGS[@]}"
}

runtime_container_run_with_copy_fallback() {
  local runtime_image="$1"
  local repo_root="$2"
  local container_workdir="$3"
  local default_output_name="$4"
  local container_repo_root="${RUNTIME_CONTAINER_FALLBACK_REPO_ROOT:-/tmp/runtime-container-repo}"
  local container_output_root="${RUNTIME_CONTAINER_FALLBACK_OUTPUT_ROOT:-/tmp/runtime-container-output}"
  local container_output_path=""
  local host_output_path=""
  local needs_output_copy=0
  local container_id=""
  local output_parent=""
  local fallback_index=0
  local container_args=()
  local fallback_workdir="${container_repo_root}"

  if [[ -n "${default_output_name}" ]]; then
    container_output_path="${container_repo_root}/${default_output_name}"
    host_output_path="${repo_root}/${default_output_name}"
    needs_output_copy=1
  fi

  if [[ ${RUNTIME_CONTAINER_OUTPUT_WAS_EXPLICIT} -eq 1 ]]; then
    if [[ ${RUNTIME_CONTAINER_OUTPUT_ARGUMENT_IS_ABSOLUTE} -eq 1 ]]; then
      host_output_path="${RUNTIME_CONTAINER_OUTPUT_ARGUMENT}"
      container_output_path="${container_output_root}${RUNTIME_CONTAINER_OUTPUT_ARGUMENT}"
    else
      host_output_path="${repo_root}/${RUNTIME_CONTAINER_OUTPUT_ARGUMENT}"
      container_output_path="${container_repo_root}/${RUNTIME_CONTAINER_OUTPUT_ARGUMENT}"
    fi
    needs_output_copy=1
  fi

  while [[ ${fallback_index} -lt ${#RUNTIME_CONTAINER_ARGS[@]} ]]; do
    local current_arg="${RUNTIME_CONTAINER_ARGS[${fallback_index}]}"

    if [[ -n "${RUNTIME_CONTAINER_REPO_ROOT_FLAG}" && "${current_arg}" == "${RUNTIME_CONTAINER_REPO_ROOT_FLAG}" ]]; then
      container_args+=("${RUNTIME_CONTAINER_REPO_ROOT_FLAG}" "${container_repo_root}")
      fallback_index=$((fallback_index + 2))
      continue
    fi

    if [[ -n "${RUNTIME_CONTAINER_REPO_ROOT_FLAG}" && "${current_arg}" == ${RUNTIME_CONTAINER_REPO_ROOT_FLAG}=* ]]; then
      container_args+=("${RUNTIME_CONTAINER_REPO_ROOT_FLAG}=${container_repo_root}")
      fallback_index=$((fallback_index + 1))
      continue
    fi

    if [[ -n "${RUNTIME_CONTAINER_OUTPUT_FLAG}" && "${current_arg}" == "${RUNTIME_CONTAINER_OUTPUT_FLAG}" && ${needs_output_copy} -eq 1 ]]; then
      container_args+=("${RUNTIME_CONTAINER_OUTPUT_FLAG}" "${container_output_path}")
      fallback_index=$((fallback_index + 2))
      continue
    fi

    if [[ -n "${RUNTIME_CONTAINER_OUTPUT_FLAG}" && "${current_arg}" == ${RUNTIME_CONTAINER_OUTPUT_FLAG}=* && ${needs_output_copy} -eq 1 ]]; then
      container_args+=("${RUNTIME_CONTAINER_OUTPUT_FLAG}=${container_output_path}")
      fallback_index=$((fallback_index + 1))
      continue
    fi

    container_args+=("${current_arg}")
    fallback_index=$((fallback_index + 1))
  done

  if [[ -n "${RUNTIME_CONTAINER_REPO_ROOT_FLAG}" && -z "${RUNTIME_CONTAINER_EXPLICIT_REPO_ROOT}" ]]; then
    container_args+=("${RUNTIME_CONTAINER_REPO_ROOT_FLAG}" "${container_repo_root}")
  fi

  if [[ -n "${RUNTIME_CONTAINER_OUTPUT_FLAG}" && ${RUNTIME_CONTAINER_OUTPUT_WAS_EXPLICIT} -eq 0 && ${needs_output_copy} -eq 1 ]]; then
    container_args+=("${RUNTIME_CONTAINER_OUTPUT_FLAG}" "${container_output_path}")
  fi

  if [[ "${container_workdir}" == "${repo_root}" ]]; then
    fallback_workdir="${container_repo_root}"
  elif [[ "${container_workdir}" == "${repo_root}"/* ]]; then
    fallback_workdir="${container_repo_root}/${container_workdir#${repo_root}/}"
  fi

  container_id="$(docker create --workdir "${fallback_workdir}" "${runtime_image}" "${container_args[@]}")"

  if ! docker cp "${repo_root}/." "${container_id}:${container_repo_root}"; then
    docker rm -f "${container_id}" >/dev/null 2>&1 || true
    return 1
  fi

  if ! docker start -a "${container_id}"; then
    docker rm -f "${container_id}" >/dev/null 2>&1 || true
    return 1
  fi

  if [[ ${needs_output_copy} -eq 1 ]]; then
    output_parent="${host_output_path%/*}"
    if [[ -z "${output_parent}" || "${output_parent}" == "${host_output_path}" ]]; then
      output_parent="."
    fi
    mkdir -p "${output_parent}"
    if ! docker cp "${container_id}:${container_output_path}" "${host_output_path}"; then
      docker rm -f "${container_id}" >/dev/null 2>&1 || true
      return 1
    fi
  fi

  docker rm -f "${container_id}" >/dev/null 2>&1 || true
}

runtime_container_run() {
  local runtime_image="$1"
  local repo_root="$2"
  local container_workdir="$3"
  local default_output_name="$4"

  if runtime_container_bind_mount_probe "${runtime_image}" "${repo_root}"; then
    runtime_container_run_with_bind_mounts "${runtime_image}" "${repo_root}" "${container_workdir}"
    return 0
  fi

  runtime_container_run_with_copy_fallback "${runtime_image}" "${repo_root}" "${container_workdir}" "${default_output_name}"
}
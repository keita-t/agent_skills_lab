#!/usr/bin/env bash
set -euo pipefail

ensure_docker_cli() {
    if command -v docker >/dev/null 2>&1; then
        return 0
    fi

    echo "Docker CLI missing — installing docker.io and docker-cli inside the dev container."
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends docker.io docker-cli
}

ensure_docker_cli

if [[ -S /var/run/docker-host.sock ]]; then
    echo "Host Docker socket detected — using docker-outside-of-docker."
    sudo ln -sf /var/run/docker-host.sock /var/run/docker.sock
    # Match the host socket's GID so the container user can access it.
    HOST_GID=$(stat -c '%g' /var/run/docker-host.sock)
    sudo groupmod -g "$HOST_GID" docker 2>/dev/null \
        || sudo groupadd -g "$HOST_GID" docker
    sudo usermod -aG docker "$(id -un)"
else
    echo "Host Docker socket not available — starting docker-in-docker."
    sudo dockerd >/tmp/dockerd.log 2>&1 &
    echo "Waiting for Docker daemon to start..."
    timeout 30 bash -c 'until docker info >/dev/null 2>&1; do sleep 1; done'
    echo "Docker daemon ready."
fi

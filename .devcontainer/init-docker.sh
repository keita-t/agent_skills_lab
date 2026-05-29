#!/usr/bin/env bash
set -euo pipefail

if [ -S /var/run/docker-host.sock ]; then
    echo "Host Docker socket detected — using docker-outside-of-docker."
    sudo ln -sf /var/run/docker-host.sock /var/run/docker.sock
    # Match the host socket's GID so the container user can access it
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

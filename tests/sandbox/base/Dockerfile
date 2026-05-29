FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements-dev.txt

CMD ["bash"]

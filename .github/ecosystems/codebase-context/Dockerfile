FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/codebase-context

COPY generate_codebase_context.py /opt/codebase-context/generate_codebase_context.py

ENTRYPOINT ["python", "/opt/codebase-context/generate_codebase_context.py"]
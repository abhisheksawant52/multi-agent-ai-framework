# syntax=docker/dockerfile:1

# ---- Builder: install the library into an isolated prefix ----
FROM python:3.14-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip \
    && pip install --prefix=/install .

# ---- Runtime: minimal, non-root image that runs the example ----
FROM python:3.14-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AGENT_LLM_PROVIDER=echo

# Create an unprivileged user to run the workload.
RUN useradd --create-home --uid 10001 agent

COPY --from=builder /install /usr/local
COPY examples ./examples

USER agent
WORKDIR /home/agent

# Cheap liveness check: the package imports and the CLI responds.
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD ["python", "-c", "import multi_agent; print(multi_agent.__version__)"]

ENTRYPOINT ["python", "/examples/two_agent_pipeline.py"]

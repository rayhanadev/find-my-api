FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

WORKDIR /app

COPY pyproject.toml uv.lock /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

COPY src/ /app/src/

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]

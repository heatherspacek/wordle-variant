FROM pypy:3-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY . /app
COPY data/* ./data
RUN uv sync --no-dev
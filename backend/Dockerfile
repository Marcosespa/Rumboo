FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PATH="/app/.venv/bin:$PATH"
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
RUN useradd --uid 10002 --create-home api && chown -R api:api /app
USER api
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && python -m app.cli bootstrap && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --workers 1"]

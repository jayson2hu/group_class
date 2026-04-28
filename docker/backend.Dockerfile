FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY apps /app/apps

ENV PYTHONPATH=/app
ENV GROUP_CLASS_BACKEND_HOST=0.0.0.0
ENV GROUP_CLASS_BACKEND_PORT=18000

EXPOSE 18000

CMD ["uv", "run", "uvicorn", "apps.group_class_backend.app:app", "--host", "0.0.0.0", "--port", "18000"]

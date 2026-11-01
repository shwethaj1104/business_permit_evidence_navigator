FROM python:3.12-slim AS build
WORKDIR /app
RUN pip install --no-cache-dir uv==0.13.0
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra azure --no-install-project --no-editable
COPY app ./app
RUN uv sync --frozen --no-dev --extra azure --no-editable

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/app/.venv/bin:$PATH"
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app app
COPY --from=build --chown=app:app /app/.venv /app/.venv
# Preserve the venv's interpreter paths when copying from the build stage.
ENV VIRTUAL_ENV=/app/.venv
USER app
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

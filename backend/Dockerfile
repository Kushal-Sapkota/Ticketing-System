FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/opt/venv
WORKDIR /build
RUN python -m venv "$VENV_PATH" && "$VENV_PATH/bin/pip" install --upgrade pip
COPY requirements.txt .
RUN "$VENV_PATH/bin/pip" install --no-cache-dir -r requirements.txt
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY app ./app
COPY scripts ./scripts
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["sh", "-c", "python scripts/seed.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

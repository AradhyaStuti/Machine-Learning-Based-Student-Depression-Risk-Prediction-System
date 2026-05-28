# Build a small image for running the FastAPI service.
# (The GUI is desktop-only and not meant to run inside the container.)

FROM python:3.12-slim

WORKDIR /app

# curl is only used by the HEALTHCHECK below
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data ./data
COPY model_files ./model_files

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fs http://localhost:${PORT:-7860}/health || exit 1

# Shell form so ${PORT} is expanded at runtime (Render/Railway/Fly/HF set $PORT)
CMD uvicorn src.api:app --host 0.0.0.0 --port ${PORT:-7860}

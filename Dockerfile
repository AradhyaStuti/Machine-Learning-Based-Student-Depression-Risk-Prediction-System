# Container that serves both the Gradio web UI (at /) and the FastAPI
# endpoints (at /health, /predict, /predictions, /docs).
# The desktop tkinter GUI is not in the container - that one is run with
# `python main.py` locally.

FROM python:3.12-slim

WORKDIR /app

# curl is only used by the HEALTHCHECK below
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY src ./src
COPY data ./data
COPY model_files ./model_files

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fs http://localhost:${PORT:-7860}/health || exit 1

# Shell form so ${PORT} is expanded at runtime (Render/Railway/Fly/HF set $PORT)
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}

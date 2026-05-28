# Container for the web app: Gradio UI at / + the FastAPI endpoints
# alongside it. The tkinter desktop GUI isn't built in - run that with
# `python main.py` locally.

FROM python:3.12-slim

WORKDIR /app

# curl is just for the HEALTHCHECK below
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

# Shell form so $PORT actually expands (Render/Railway/Fly/HF set it for us)
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}

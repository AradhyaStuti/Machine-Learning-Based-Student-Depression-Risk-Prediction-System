# Container for the Gradio web app and FastAPI API.
# The Tkinter desktop GUI is run locally with `python main.py`.

FROM python:3.12-slim

WORKDIR /app

# Install curl for the health check
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY src ./src
COPY data ./data
COPY model_files ./model_files

# Gradio / FastAPI runs on port 7860
EXPOSE 7860

# Check whether the application is healthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fs http://localhost:${PORT:-7860}/health || exit 1

# Start the Gradio + FastAPI application
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}
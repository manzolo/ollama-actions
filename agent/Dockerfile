FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (curl for healthchecks/testing if needed)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and tests
COPY src/ /app/src/
COPY tests/ /app/tests/

# Set python path
ENV PYTHONPATH=/app

# Run with Gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${APP_PORT} --chdir src main:app"]

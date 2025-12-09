FROM python:3.11-slim

WORKDIR /app

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/

# Set python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE ${USER_SERVICE_PORT}

# Run with Gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${USER_SERVICE_PORT} --chdir src app:app"]

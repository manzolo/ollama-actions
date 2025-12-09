FROM python:3.9-slim

WORKDIR /app

COPY ollama-cli.py .

RUN pip install requests

ENTRYPOINT ["python3", "ollama-cli.py"]

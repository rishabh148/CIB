
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG SERVICE=backend
ENV SERVICE=${SERVICE}

COPY ${SERVICE}/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend /app/backend
COPY frontend /app/frontend
COPY run.py /app/run.py

EXPOSE 8000 8501

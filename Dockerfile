
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY backend/requirements.txt /tmp/backend-requirements.txt
COPY frontend/requirements.txt /tmp/frontend-requirements.txt

RUN pip install --no-cache-dir -r /tmp/backend-requirements.txt \
    && pip install --no-cache-dir -r /tmp/frontend-requirements.txt

COPY backend /app/backend
COPY frontend /app/frontend
COPY run.py /app/run.py

EXPOSE 8000 8501

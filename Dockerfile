
# Stage 1: Build the backend
FROM python:3.10-slim-buster as backend-builder

WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

# Stage 2: Build the frontend
FROM python:3.10-slim-buster as frontend-builder

WORKDIR /app/frontend
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY frontend/ .

# Stage 3: Final image
FROM python:3.10-slim-buster

WORKDIR /app

# Copy backend from builder
COPY --from=backend-builder /app/backend /app/backend

# Copy frontend from builder
COPY --from=frontend-builder /app/frontend /app/frontend

# Copy run.py and .env (if exists)
COPY run.py .
COPY .env . || true

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Set PYTHONPATH for both backend and frontend
ENV PYTHONPATH=/app

# Command to run the application using run.py
# CMD ["python", "run.py"] # This will be handled by Gunicorn in docker-compose.yml

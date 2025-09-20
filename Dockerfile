# Multi-stage Dockerfile für LaTeX Converter

# Stage 1: Base Image mit Python und LaTeX
FROM python:3.9-slim as base

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    # LaTeX-Distribution
    texlive-full \
    texlive-latex-extra \
    texlive-fonts-recommended \
    # System-Tools
    curl \
    wget \
    git \
    # Build-Tools
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Python Dependencies
FROM base as python-deps

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Production Image
FROM python-deps as production

# Arbeitsverzeichnis
WORKDIR /app

# Anwendung kopieren
COPY . .

# Verzeichnisse erstellen
RUN mkdir -p logs models cache

# Benutzer erstellen (Sicherheit)
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

# Port freigeben
EXPOSE 5000

# Health Check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Als nicht-root Benutzer ausführen
USER appuser

# Umgebungsvariablen
ENV FLASK_ENV=production \
    FLASK_APP=app.py \
    PYTHONPATH=/app \
    MODEL_CACHE_DIR=/app/models \
    LOG_FILE=/app/logs/app.log

# Start-Kommando
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]

# Stage 4: Development Image
FROM python-deps as development

WORKDIR /app

# Development-Dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    ipython

# Anwendung kopieren
COPY . .

# Verzeichnisse erstellen
RUN mkdir -p logs models cache

# Port freigeben
EXPOSE 5000

# Umgebungsvariablen für Development
ENV FLASK_ENV=development \
    FLASK_DEBUG=1 \
    FLASK_APP=app.py \
    PYTHONPATH=/app \
    MODEL_CACHE_DIR=/app/models \
    LOG_FILE=/app/logs/app.log

# Start-Kommando für Development
CMD ["python", "app.py"]

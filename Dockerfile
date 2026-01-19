# Railway Deployment - AI Speech Enhancement System v2.1
FROM python:3.12.1-slim

# Set working directory
WORKDIR /app

# Set environment variables FIRST (before any commands)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_APP=app_production.py

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    libsndfile1-dev \
    ffmpeg \
    libopenblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Upgrade pip before installing requirements
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first (better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies with retry
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p uploads outputs static/spectrograms training_data_generated && \
    chown -R nobody:nogroup /app

# Use non-root user for security
USER nobody

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health', timeout=5).read()" || exit 1

# Expose port
EXPOSE 5000

# Direct startup command - no entrypoint script needed
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--worker-class", "sync", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app_production:app"]

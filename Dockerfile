# Railway Deployment - Optimized for Speech Enhancement System
FROM python:3.12.1-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p uploads outputs static/spectrograms

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=wsgi.py

# Expose port
EXPOSE 5000

# Run with gunicorn - explicit port binding for Railway
CMD exec gunicorn --bind 0.0.0.0:5000 --workers 1 --worker-class sync --timeout 120 --access-logfile - --error-logfile - wsgi:app

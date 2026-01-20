#!/bin/bash
# Entrypoint script for Railway deployment
set -e

# Get PORT from environment or default to 5000
PORT=${PORT:-5000}

echo "========================================="
echo "Starting AI Speech Enhancement System v2.1"
echo "========================================="
echo "PORT: $PORT"
echo "Environment: Production"
echo "Python: $(python --version)"
echo "Directory: $(pwd)"
echo "========================================="

# Create necessary directories
mkdir -p uploads outputs static/spectrograms

# Run gunicorn with optimized settings for Railway
# Removed --preload-app for faster startup and better healthcheck response
exec gunicorn \
    --bind 0.0.0.0:${PORT} \
    --workers 1 \
    --threads 2 \
    --worker-class gthread \
    --timeout 300 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    app_production:app

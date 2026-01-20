#!/bin/bash
# Entrypoint script for Railway deployment
set -e

# Get PORT from environment or default to 5000
PORT=${PORT:-5000}

# CRITICAL: Set numba environment variables BEFORE Python starts
export NUMBA_DISABLE_JIT=1
export NUMBA_CACHE_DIR=/tmp/numba_cache
export NUMBA_WARNINGS=0
export PYTHONWARNINGS=ignore

echo "========================================="
echo "Starting AI Speech Enhancement System v2.1"
echo "========================================="
echo "PORT: $PORT"
echo "Environment: Production"
echo "Python: $(python --version)"
echo "Directory: $(pwd)"
echo "NUMBA_DISABLE_JIT: $NUMBA_DISABLE_JIT (MUST BE 1)"
echo "NUMBA_CACHE_DIR: $NUMBA_CACHE_DIR"
echo "========================================="

# Create necessary directories
mkdir -p uploads outputs static/spectrograms

# Run gunicorn with optimized settings for Railway
# Using wsgi_production.py to ensure env vars are set before any imports
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
    wsgi_production:app
